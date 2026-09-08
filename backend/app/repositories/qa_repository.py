from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base_repository import BaseRepository


class QARepository(BaseRepository):
    async def create_query(
        self,
        session: AsyncSession,
        product_id: int,
        query: str,
        response: str,
    ) -> dict[str, Any]:
        result = await self.execute_query(
            session,
            "qa",
            "create_query",
            {"product_id": product_id, "query": query, "response": response},
        )
        return dict(result.mappings().one())
