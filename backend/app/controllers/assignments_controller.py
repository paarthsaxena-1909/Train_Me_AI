from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.db.session import DbSession
from app.models.assignments import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentSubmit,
    AssignmentSummaryResponse,
)
from app.security.dependencies import CurrentAgent
from app.services.assignments import AssignmentsService


router = APIRouter(prefix="/api/v1/assignments", tags=["assignments"])


async def get_service() -> AssignmentsService:
    return AssignmentsService()


ServiceDependency = Annotated[AssignmentsService, Depends(get_service)]


@router.post("", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    payload: AssignmentCreate,
    session: DbSession,
    principal: CurrentAgent,
    service: ServiceDependency,
) -> AssignmentResponse:
    return await service.create(session, principal, payload)


@router.get("", response_model=list[AssignmentSummaryResponse])
async def list_assignments(
    session: DbSession,
    principal: CurrentAgent,
    service: ServiceDependency,
    product_lineup_id: int | None = Query(default=None, gt=0),
) -> list[AssignmentSummaryResponse]:
    return await service.list(session, principal, product_lineup_id)


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int,
    session: DbSession,
    principal: CurrentAgent,
    service: ServiceDependency,
) -> AssignmentResponse:
    return await service.get(session, principal, assignment_id)


@router.post("/{assignment_id}/submit", response_model=AssignmentResponse)
async def submit_assignment(
    assignment_id: int,
    payload: AssignmentSubmit,
    session: DbSession,
    principal: CurrentAgent,
    service: ServiceDependency,
) -> AssignmentResponse:
    return await service.submit(session, principal, assignment_id, payload)
