import asyncio

import pytest

from app.errors import NotFoundError
from app.models.qa import QueryCreate, QueryResponse
from app.services.qa_service import QAService


class Session:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    async def commit(self):
        self.commits += 1

    async def rollback(self):
        self.rollbacks += 1


class Repo:
    def __init__(self):
        self.saved = None

    async def create_query(self, session, product_id, query, response):
        self.saved = {"id": 1, "product_id": product_id, "query": query, "response": response}
        return self.saved


class ProductContext:
    def __init__(self, exists=True):
        self.exists = exists

    async def get_product_context(self, product_id):
        if not self.exists:
            raise NotFoundError("Product not found")
        return {"product": {"id": product_id}, "variants": []}


def test_ask_persists_one_mock_answer_for_a_product():
    async def run():
        repository = Repo()
        session = Session()
        result = await QAService(repository, ProductContext()).ask(session, QueryCreate(product_id=7, query="What is the battery life?"))

        assert isinstance(result, QueryResponse)
        assert result.id == 1
        assert result.product_id == 7
        assert result.response == "Mock AI response based on the selected product specifications."
        assert repository.saved["query"] == "What is the battery life?"
        assert session.commits == 1

    asyncio.run(run())


def test_ask_rejects_unknown_product():
    async def run():
        with pytest.raises(NotFoundError):
            await QAService(Repo(), ProductContext(exists=False)).ask(Session(), QueryCreate(product_id=99, query="Anything?"))

    asyncio.run(run())
