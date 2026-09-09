from app.repositories.base_repository import BaseRepository

class AssignmentsRepository(BaseRepository):
    async def lineup_context(self, session, lineup_id):
        return (await self.execute_query(session, "assignments", "get_lineup_context", {"product_lineup_id": lineup_id})).mappings().all()
    async def create(self, session, lineup_id):
        return (await self.execute_query(session, "assignments", "create_assignment", {"product_lineup_id": lineup_id})).mappings().one()
    async def map_agent(self, session, assignment_id, agent_id):
        await self.execute_query(session, "assignments", "create_mapping", {"assignment_id": assignment_id, "agent_id": agent_id})
    async def create_question(self, session, assignment_id, number, question):
        return (await self.execute_query(session, "assignments", "create_question", {"assignment_id": assignment_id, "question_number": number, "question": question})).mappings().one()
    async def list(self, session, agent_id, lineup_id=None):
        return (await self.execute_query(session, "assignments", "list_assignments", {"agent_id": agent_id, "product_lineup_id": lineup_id})).mappings().all()
    async def get(self, session, assignment_id, agent_id):
        return (await self.execute_query(session, "assignments", "get_assignment", {"assignment_id": assignment_id, "agent_id": agent_id})).mappings().all()
    async def submit_question(self, session, assignment_id, question_id, answer, evaluation):
        await self.execute_query(session, "assignments", "submit_question", {"assignment_id": assignment_id, "question_id": question_id, "answer": answer, "evaluation": evaluation})
    async def complete(self, session, assignment_id, evaluation):
        await self.execute_query(session, "assignments", "complete_assignment", {"assignment_id": assignment_id})
