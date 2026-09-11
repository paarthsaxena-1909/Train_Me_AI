import asyncio
from typing import Any
from unittest.mock import Mock

import httpx
import pytest

from app.main import create_app
from app.models.auth import Principal
from app.models.evaluations import AvatarSessionResponse, EvaluationMessageResponse
from app.security.dependencies import require_agent
from app.services.evaluations.evaluation_functions import MOCK_RESPONSES, select_mock_response
from app.services.evaluations import evaluation_functions
from app.services.evaluations.evaluation_graph import evaluation_graph
from app.services.evaluations.evaluation_service import EvaluationService
from app.settings import Settings


def test_mock_response_is_selected_from_the_fixed_catalog() -> None:
    response = select_mock_response("Tell me about customer service")

    assert len(MOCK_RESPONSES) == 10
    assert response in MOCK_RESPONSES


def test_evaluation_graph_returns_a_mock_response() -> None:
    result = evaluation_graph.invoke({"message": "How should I greet a customer?"})

    assert result["response_text"] in MOCK_RESPONSES


class ASGIClient:
    def __init__(self, application: Any) -> None:
        self.application = application

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        async def send() -> httpx.Response:
            transport = httpx.ASGITransport(app=self.application)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                return await client.post(path, **kwargs)

        return asyncio.run(send())


class StubEvaluationService:
    async def create_avatar_session(self) -> AvatarSessionResponse:
        return AvatarSessionResponse(session_token="temporary-token", session_id="session-1", api_url="https://api.liveavatar.com")

    async def respond(self, message: str) -> EvaluationMessageResponse:
        return EvaluationMessageResponse(response_text=MOCK_RESPONSES[0])


def build_client() -> ASGIClient:
    from app.controllers.evaluations_controller import get_evaluation_service

    application = create_app()

    async def override_agent() -> Principal:
        return Principal(account_id=1, role="agent")

    async def override_service() -> StubEvaluationService:
        return StubEvaluationService()

    application.dependency_overrides[require_agent] = override_agent
    application.dependency_overrides[get_evaluation_service] = override_service
    return ASGIClient(application)


def test_agent_evaluation_routes_return_temporary_avatar_data_and_a_mock_reply() -> None:
    client = build_client()

    session_response = client.post("/api/v1/evaluations/avatar-session")
    message_response = client.post("/api/v1/evaluations/message", json={"message": "Hello avatar"})

    assert session_response.status_code == 200
    assert session_response.json() == {
        "session_token": "temporary-token",
        "session_id": "session-1",
        "api_url": "https://api.liveavatar.com",
    }
    assert message_response.status_code == 200
    assert message_response.json()["response_text"] in MOCK_RESPONSES


def test_evaluation_service_uses_the_graph_without_a_database() -> None:
    async def run() -> None:
        result = await EvaluationService().respond("Help me greet a customer")

        assert result.response_text in MOCK_RESPONSES

    asyncio.run(run())


def test_existing_heygen_avatar_name_environment_key_maps_to_the_avatar_id_setting(monkeypatch) -> None:
    monkeypatch.setenv("HEYGEN_AVATAR_ID", "")
    monkeypatch.setenv("HEYGEN_AVATAR_NAME", "avatar-id-from-existing-env-file")
    settings = Settings()

    assert settings.heygen_avatar_id == "avatar-id-from-existing-env-file"


def test_heygen_failures_log_upstream_status_without_sensitive_headers(monkeypatch, capsys: pytest.CaptureFixture[str]) -> None:
    class FailingClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

        async def post(self, *args, **kwargs):
            request = httpx.Request("POST", "https://api.liveavatar.com/v1/sessions/token")
            response = httpx.Response(400, request=request, text='{"error":"invalid avatar"}')
            raise httpx.HTTPStatusError("bad request", request=request, response=response)

    monkeypatch.setattr(evaluation_functions.httpx, "AsyncClient", lambda **kwargs: FailingClient())
    error_log = Mock()
    monkeypatch.setattr(evaluation_functions.logger, "error", error_log)
    settings = Settings(heygen_api_key="api-secret", heygen_avatar_id="avatar-123")

    with pytest.raises(Exception, match="HeyGen avatar session could not be created"):
        asyncio.run(evaluation_functions.request_heygen_session(settings))

    message = error_log.call_args.args[0] % error_log.call_args.args[1:]
    assert "HeyGen avatar session request failed" in message
    assert "status_code=400" in message
    assert "upstream_error=invalid avatar" in message
    assert "api-secret" not in message


def test_heygen_connection_failures_log_exception_detail(monkeypatch) -> None:
    class FailingClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

        async def post(self, *args, **kwargs):
            request = httpx.Request("POST", "https://api.liveavatar.com/v1/sessions/token")
            raise httpx.ConnectError("temporary DNS failure", request=request)

    monkeypatch.setattr(evaluation_functions.httpx, "AsyncClient", lambda **kwargs: FailingClient())
    error_log = Mock()
    monkeypatch.setattr(evaluation_functions.logger, "error", error_log)
    settings = Settings(heygen_api_key="api-secret", heygen_avatar_id="avatar-123")

    with pytest.raises(Exception, match="HeyGen avatar session could not be created"):
        asyncio.run(evaluation_functions.request_heygen_session(settings))

    message = error_log.call_args.args[0] % error_log.call_args.args[1:]
    assert "error_type=ConnectError" in message
    assert "error=temporary DNS failure" in message
    assert "api-secret" not in message


def test_heygen_full_mode_request_includes_avatar_persona(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    class SuccessfulClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

        async def post(self, *args, **kwargs):
            captured.update(kwargs)
            request = httpx.Request("POST", "https://api.liveavatar.com/v1/sessions/token")
            return httpx.Response(
                200,
                request=request,
                json={"data": {"session_token": "temporary-token", "session_id": "session-1"}},
            )

    monkeypatch.setattr(evaluation_functions.httpx, "AsyncClient", lambda **kwargs: SuccessfulClient())
    debug_log = Mock()
    monkeypatch.setattr(evaluation_functions.logger, "debug", debug_log)
    settings = Settings(heygen_api_key="api-secret", heygen_avatar_id="avatar-123")

    result = asyncio.run(evaluation_functions.request_heygen_session(settings))

    assert result == {"session_token": "temporary-token", "session_id": "session-1"}
    assert captured["json"] == {
        "mode": "FULL",
        "avatar_id": "avatar-123",
        "avatar_persona": {},
        "is_sandbox": False,
    }
    debug_messages = [call.args[0] % call.args[1:] for call in debug_log.call_args_list]
    assert any("outbound request prepared" in message for message in debug_messages)
    assert any("response received status_code=200" in message for message in debug_messages)
