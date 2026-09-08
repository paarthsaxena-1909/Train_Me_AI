from pydantic import ConfigDict, validate_call
from typing import Any

from app.logger import AppLogger
from app.models.qa import QueryCreate, QueryResponse
from app.orchestration.ports import ProductContextPort
from app.repositories.qa_repository import QARepository


MOCK_RESPONSE = "Mock AI response based on the selected product specifications."


class QAService:
    def __init__(
        self,
        repository: QARepository | None = None,
        product_context: ProductContextPort | None = None,
    ) -> None:
        self.repository = repository or QARepository()
        self.product_context = product_context
        self.logger = AppLogger.get_logger(__name__)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True), validate_return=True)
    async def ask(self, session: Any, payload: QueryCreate) -> QueryResponse:
        query = payload.query.strip()
        if self.product_context is None:
            raise RuntimeError("A product context port is required")
        await self.product_context.get_product_context(payload.product_id)
        try:
            row = await self.repository.create_query(
                session, payload.product_id, query, MOCK_RESPONSE
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        self.logger.info("agent query created product_id=%s query_id=%s", payload.product_id, row["id"])
        return QueryResponse.model_validate(row)
