from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health import HealthResponse
from app.repositories.health_repository import HealthRepository


class HealthService:
    def __init__(self, repository: HealthRepository) -> None:
        self.repository = repository

    async def check(self, session: AsyncSession) -> HealthResponse:
        database_time = await self.repository.get_database_time(session)
        return HealthResponse(status="ok", database_time=database_time)
