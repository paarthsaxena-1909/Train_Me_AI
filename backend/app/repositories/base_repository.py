from collections.abc import Mapping
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.query_loader import load_query


class BaseRepository:
    """Shared persistence helpers for repositories."""

    @staticmethod
    def load_query(service: str, query_name: str) -> str:
        return load_query(service, query_name)

    async def execute_query(
        self,
        session: AsyncSession,
        service: str,
        query_name: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> Result[Any]:
        """Load and execute a named SQL query with bound parameters."""
        return await session.execute(text(self.load_query(service, query_name)), parameters or {})
