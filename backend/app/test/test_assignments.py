import asyncio
from pathlib import Path
import pytest
from app.errors import ConflictError, NotFoundError
from app.models.assignments import AssignmentCreate, AssignmentSubmit, AssignmentAnswer
from app.models.auth import Principal
from app.services.assignments import AssignmentsService
from app.services.assignments.assignment_generator_ai import MockAssignmentGenerator

class Session:
    def __init__(self): self.commits = 0
    async def commit(self): self.commits += 1

class Repo:
    def __init__(self):
        self.assignment = {"id": 10, "product_lineup_id": 3, "status": None}
        self.questions = [{"question_id": 1, "question_number": 1, "question": "Q1", "answer": None, "evaluation": None}, {"question_id": 2, "question_number": 2, "question": "Q2", "answer": None, "evaluation": None}]
        self.completed = False
    async def lineup_context(self, session, lineup_id): return [{"lineup_identifier": "Phone lineup"}] if lineup_id == 3 else []
    async def create(self, session, lineup_id): return self.assignment
    async def map_agent(self, session, assignment_id, agent_id): self.mapped = (assignment_id, agent_id)
    async def create_question(self, session, assignment_id, number, question): return {"id": number}
    async def get(self, session, assignment_id, agent_id):
        if assignment_id != 10 or getattr(self, "mapped", (10, agent_id))[1] != agent_id: return []
        return [{**self.assignment, "lineup_identifier": "Phone lineup", **question} for question in self.questions]
    async def submit_question(self, session, *args): self.questions[args[1] - 1].update(answer=args[2], evaluation=args[3])
    async def complete(self, session, assignment_id, evaluation): self.completed = True; self.assignment["status"] = "completed"
    async def status(self, session, assignment_id, agent_id): return self.assignment["status"] if agent_id == 4 else None

def test_create_maps_assignment_to_authenticated_agent_and_generates_questions():
    async def run():
        repo, session = Repo(), Session()
        result = await AssignmentsService(repo).create(session, Principal(account_id=4, role="agent"), AssignmentCreate(product_lineup_id=3))
        assert result.product_lineup_id == 3 and repo.mapped == (10, 4) and len(result.questions) == 2
    asyncio.run(run())

def test_mock_generator_returns_ten_questions():
    questions = MockAssignmentGenerator().generate([{"lineup_identifier": "Phone lineup"}])
    assert len(questions) == 10
    assert [question.question_number for question in questions] == list(range(1, 11))

def test_submit_requires_every_question_and_completes_once():
    async def run():
        repo, session, principal = Repo(), Session(), Principal(account_id=4, role="agent")
        repo.mapped = (10, 4)
        service = AssignmentsService(repo)
        with pytest.raises(ConflictError): await service.submit(session, principal, 10, AssignmentSubmit(answers=[AssignmentAnswer(question_id=1, answer="a")]))
        result = await service.submit(session, principal, 10, AssignmentSubmit(answers=[AssignmentAnswer(question_id=1, answer="a"), AssignmentAnswer(question_id=2, answer="b")]))
        assert result.status == "completed" and all(question.evaluation for question in result.questions)
        with pytest.raises(ConflictError): await service.submit(session, principal, 10, AssignmentSubmit(answers=[AssignmentAnswer(question_id=1, answer="a"), AssignmentAnswer(question_id=2, answer="b")]))
    asyncio.run(run())

def test_assignment_schema_removes_question_product_id():
    source = Path("database/models/schema.py").read_text()
    assert "class AssignmentQuestion" in source and "product_id" not in source.split("class AssignmentQuestion", 1)[1].split("class AssignmentAgentMapping", 1)[0]

def test_assignment_has_no_aggregate_evaluation_fields():
    source = Path("database/models/schema.py").read_text()
    assignment = source.split("class Assignment", 1)[1].split("class AssignmentQuestion", 1)[0]
    assert all(field not in assignment for field in ("score", "strengths", "missing_concepts", "overall_feedback", "limitation"))

def test_assignment_indexes_match_current_access_patterns():
    from database.models.schema import Assignment, AssignmentAgentMapping, AssignmentQuestion

    assert "ix_assignments_product_lineup_id" in {index.name for index in Assignment.__table__.indexes}
    assert "ix_assignments_status" in {index.name for index in Assignment.__table__.indexes}
    assert "ix_assignment_questions_assignment_id" in {index.name for index in AssignmentQuestion.__table__.indexes}
    assert "uq_assignment_agent_mapping_pair" in {constraint.name for constraint in AssignmentAgentMapping.__table__.constraints}

def test_assignment_list_query_types_optional_lineup_parameter_for_postgres():
    sql = Path("app/queries/postgres/assignments/list_assignments.sql").read_text()
    assert "CAST(:product_lineup_id AS INTEGER)" in sql

def test_assignment_question_persists_generated_question_text_in_single_migration():
    model = Path("database/models/schema.py").read_text()
    migration = Path("database/versions/0005_assignments_lineup_workflow.py").read_text()
    insert_query = Path("app/queries/postgres/assignments/create_question.sql").read_text()
    assert "question: Mapped[str]" in model
    assert 'sa.Column("question", sa.Text()' in migration
    assert "INSERT INTO assignment_questions" in insert_query
    assert ":question" in insert_query
