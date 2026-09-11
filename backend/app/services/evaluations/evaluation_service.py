"""Application service for the stateless evaluation-avatar prototype."""

from pydantic import ConfigDict, validate_call

from app.errors import AppError
from app.logger import AppLogger
from app.models.evaluations import AvatarSessionResponse, EvaluationMessageResponse
from app.services.evaluations.evaluation_functions import request_heygen_session
from app.services.evaluations.evaluation_graph import evaluation_graph
from app.settings import Settings, get_settings


class EvaluationService:
    """Coordinate the graph and server-only HeyGen session creation."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.logger = AppLogger.get_logger(__name__)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True), validate_return=True)
    async def create_avatar_session(self) -> AvatarSessionResponse:
        if not self.settings.heygen_api_key or not self.settings.heygen_avatar_id:
            self.logger.error(
                "avatar session configuration incomplete api_key_configured=%s avatar_id_configured=%s",
                bool(self.settings.heygen_api_key),
                bool(self.settings.heygen_avatar_id),
            )
            raise AppError("HEYGEN_API_KEY and HEYGEN_AVATAR_ID must be configured to start an avatar session")
        self.logger.debug(
            "avatar session configuration ready api_url=%s avatar_id=%s sandbox=%s",
            self.settings.heygen_api_url,
            self.settings.heygen_avatar_id,
            self.settings.heygen_is_sandbox,
        )
        payload = await request_heygen_session(self.settings)
        self.logger.info("avatar session created session_id=%s", payload["session_id"])
        return AvatarSessionResponse.model_validate({
            "session_token": payload["session_token"],
            "session_id": payload["session_id"],
            "api_url": self.settings.heygen_api_url,
        })

    @validate_call(validate_return=True)
    async def respond(self, message: str) -> EvaluationMessageResponse:
        result = evaluation_graph.invoke({"message": message})
        return EvaluationMessageResponse.model_validate(result)
