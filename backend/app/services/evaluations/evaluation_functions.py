"""Side-effecting and leaf functions invoked by the evaluation graph."""

from random import choice
from typing import Protocol

import httpx

from app.errors import AppError
from app.logger import AppLogger


MOCK_RESPONSES = (
    "That is a great start. Keep your answer clear and focused on the customer's need.",
    "I would explain the key benefit first, then connect it to what the customer has told me.",
    "Good question. A confident, simple explanation helps customers make decisions faster.",
    "Try asking one follow-up question so you can recommend the most relevant option.",
    "I would acknowledge the concern, share the practical benefit, and then check whether that helps.",
    "That approach sounds helpful. Use plain language and avoid overwhelming the customer with details.",
    "A strong response begins with listening, then gives the customer a specific next step.",
    "You can make that answer even better by giving one short example from a real customer situation.",
    "Focus on the outcome for the customer, not just the product feature itself.",
    "Nice thinking. End by inviting the customer to ask anything else they would like to know.",
)

logger = AppLogger.get_logger(__name__)


def select_mock_response(message: str) -> str:
    """Return one prototype response while preserving the future LLM boundary."""
    if not message.strip():
        raise ValueError("message must not be empty")
    return choice(MOCK_RESPONSES)


class HeyGenSettings(Protocol):
    heygen_api_key: str
    heygen_api_url: str
    heygen_avatar_id: str
    heygen_is_sandbox: bool


def _safe_upstream_error(response: httpx.Response) -> str:
    """Extract a short diagnostic without logging an upstream token payload."""
    try:
        payload = response.json()
    except ValueError:
        return response.text[:200].replace("\n", " ")
    if isinstance(payload, dict):
        for key in ("error", "message", "detail", "code"):
            value = payload.get(key)
            if isinstance(value, str):
                return value[:500]
    return "structured error response"


async def request_heygen_session(settings: HeyGenSettings) -> dict[str, str]:
    """Mint a temporary FULL-mode LiveAvatar session token without exposing the API key."""
    endpoint = f"{settings.heygen_api_url.rstrip('/')}/v1/sessions/token"
    logger.info(
        "HeyGen avatar session request started api_url=%s avatar_id=%s is_sandbox=%s",
        settings.heygen_api_url,
        settings.heygen_avatar_id,
        settings.heygen_is_sandbox,
    )
    logger.debug(
        "HeyGen avatar session outbound request prepared endpoint=%s timeout_seconds=%s payload_fields=%s",
        endpoint,
        20,
        "mode,avatar_id,avatar_persona,is_sandbox",
    )
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                endpoint,
                headers={"X-API-KEY": settings.heygen_api_key, "Content-Type": "application/json"},
                json={
                    "mode": "FULL",
                    "avatar_id": settings.heygen_avatar_id,
                    "avatar_persona": {},
                    "is_sandbox": settings.heygen_is_sandbox,
                },
            )
            logger.debug("HeyGen avatar session response received status_code=%s", response.status_code)
            response.raise_for_status()
            response_payload = response.json()
            logger.debug(
                "HeyGen avatar session response parsed top_level_fields=%s data_fields=%s",
                ",".join(sorted(response_payload)) if isinstance(response_payload, dict) else "none",
                ",".join(sorted(response_payload.get("data", {})))
                if isinstance(response_payload, dict) and isinstance(response_payload.get("data"), dict)
                else "none",
            )
            data = response_payload.get("data", {})
    except httpx.HTTPStatusError as error:
        logger.error(
            "HeyGen avatar session request failed status_code=%s upstream_error=%s",
            error.response.status_code,
            _safe_upstream_error(error.response),
        )
        raise AppError("HeyGen avatar session could not be created") from error
    except httpx.RequestError as error:
        logger.error(
            "HeyGen avatar session request failed error_type=%s error=%s",
            type(error).__name__,
            str(error),
        )
        raise AppError("HeyGen avatar session could not be created") from error
    except ValueError as error:
        logger.error("HeyGen avatar session response was not valid JSON")
        raise AppError("HeyGen avatar session could not be created") from error

    session_token = data.get("session_token")
    session_id = data.get("session_id")
    if not isinstance(session_token, str) or not isinstance(session_id, str):
        logger.error("HeyGen avatar session response missing required fields")
        raise AppError("HeyGen returned an invalid avatar session")
    logger.info("HeyGen avatar session request succeeded session_id=%s", session_id)
    return {"session_token": session_token, "session_id": session_id}
