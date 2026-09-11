"""HTTP endpoints for the agent-only evaluation-avatar prototype."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.models.evaluations import AvatarSessionResponse, EvaluationMessageRequest, EvaluationMessageResponse
from app.logger import AppLogger
from app.security.dependencies import CurrentAgent
from app.services.evaluations.evaluation_service import EvaluationService


router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])
logger = AppLogger.get_logger(__name__)


def get_evaluation_service() -> EvaluationService:
    return EvaluationService()


ServiceDependency = Annotated[EvaluationService, Depends(get_evaluation_service)]


@router.post("/avatar-session", response_model=AvatarSessionResponse)
async def create_avatar_session(principal: CurrentAgent, service: ServiceDependency) -> AvatarSessionResponse:
    logger.info("avatar session request started account_id=%s role=%s", principal.account_id, principal.role)
    response = await service.create_avatar_session()
    logger.info("avatar session request succeeded account_id=%s session_id=%s", principal.account_id, response.session_id)
    return response


@router.post("/message", response_model=EvaluationMessageResponse)
async def send_message(
    payload: EvaluationMessageRequest,
    principal: CurrentAgent,
    service: ServiceDependency,
) -> EvaluationMessageResponse:
    logger.info(
        "avatar message request started account_id=%s role=%s message_length=%s",
        principal.account_id,
        principal.role,
        len(payload.message),
    )
    response = await service.respond(payload.message)
    logger.info("avatar message request succeeded account_id=%s response_length=%s", principal.account_id, len(response.response_text))
    return response
