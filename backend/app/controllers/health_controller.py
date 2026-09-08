from fastapi import APIRouter

from app.db.session import DbSession
from app.models.health import HealthResponse
from app.repositories.health_repository import HealthRepository
from app.services.health_service import HealthService


router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(session: DbSession) -> HealthResponse:
    return await HealthService(repository=HealthRepository()).check(session)
