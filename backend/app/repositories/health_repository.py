from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base_repository import BaseRepository


class HealthRepository(BaseRepository):
    async def get_database_time(self, session: AsyncSession) -> datetime:
        result = await self.execute_query(session, "health", "database_time")
        return result.scalar_one()
