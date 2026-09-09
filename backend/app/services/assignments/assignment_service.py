"""Business workflow for agent-owned assignments."""

from typing import Any

from pydantic import ConfigDict, validate_call

from app.errors import ConflictError, NotFoundError
from app.models.assignments import AssignmentCreate, AssignmentResponse, AssignmentSubmit, AssignmentSummaryResponse
from app.models.auth import Principal
from app.repositories.assignments_repository import AssignmentsRepository
from app.services.assignments.assignment_evaluator_ai import MockAssignmentEvaluator
from app.services.assignments.assignment_generator_ai import MockAssignmentGenerator


class AssignmentsService:
    def __init__(self, repository=None, generator=None, evaluator=None):
        self.repository = repository or AssignmentsRepository()
        self.generator = generator or MockAssignmentGenerator()
        self.evaluator = evaluator or MockAssignmentEvaluator()

    def _response(self, rows) -> AssignmentResponse:
        if not rows:
            raise NotFoundError("Assignment not found")
        first = dict(rows[0])
        questions = [
            {"id": row["question_id"], "question_number": row["question_number"], "question": row["question"], "answer": row["answer"], "evaluation": row["evaluation"]}
            for row in rows if row["question_id"] is not None
        ]
        return AssignmentResponse.model_validate({**first, "questions": questions})

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True), validate_return=True)
    async def create(self, session: Any, principal: Principal, payload: AssignmentCreate) -> AssignmentResponse:
        context = await self.repository.lineup_context(session, payload.product_lineup_id)
        if not context:
            raise NotFoundError("Product lineup not found")
        assignment = await self.repository.create(session, payload.product_lineup_id)
        try:
            await self.repository.map_agent(session, assignment["id"], principal.account_id)
            for question in self.generator.generate([dict(row) for row in context]):
                await self.repository.create_question(session, assignment["id"], question.question_number, question.question)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        return await self.get(session, principal, assignment["id"])

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True), validate_return=True)
    async def list(self, session: Any, principal: Principal, product_lineup_id: int | None = None) -> list[AssignmentSummaryResponse]:
        rows = await self.repository.list(session, principal.account_id, product_lineup_id)
        return [AssignmentSummaryResponse.model_validate(row) for row in rows]

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True), validate_return=True)
    async def get(self, session: Any, principal: Principal, assignment_id: int) -> AssignmentResponse:
        return self._response(await self.repository.get(session, assignment_id, principal.account_id))

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True), validate_return=True)
    async def submit(self, session: Any, principal: Principal, assignment_id: int, payload: AssignmentSubmit) -> AssignmentResponse:
        current = await self.get(session, principal, assignment_id)
        if current.status == "completed":
            raise ConflictError("Assignment has already been submitted")
        answers = {answer.question_id: answer.answer for answer in payload.answers}
        expected = {question.id for question in current.questions}
        if set(answers) != expected:
            raise ConflictError("Every assignment question must be answered exactly once")
        evaluations = self.evaluator.evaluate([{**question.model_dump(), "answer": answers[question.id]} for question in current.questions])
        try:
            for question in current.questions:
                await self.repository.submit_question(session, assignment_id, question.id, answers[question.id], evaluations[question.id])
            await self.repository.complete(session, assignment_id, None)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        return await self.get(session, principal, assignment_id)
