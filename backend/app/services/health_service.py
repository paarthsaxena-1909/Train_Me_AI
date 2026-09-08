from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health import HealthResponse
from app.logger import AppLogger
from app.repositories.health_repository import HealthRepository


logger = AppLogger.get_logger(__name__)


class HealthService:
    def __init__(self, repository: HealthRepository) -> None:
        self.repository = repository

    async def check(self, session: AsyncSession) -> HealthResponse:
        database_time = await self.repository.get_database_time(session)
        logger.info("health check succeeded")
        return HealthResponse(status="ok", database_time=database_time)
