import asyncio
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.errors import AppError, ConflictError, ForbiddenError, NotFoundError
from app.main import create_app
from app.orchestration.mediator import (
    DuplicateRouteError,
    MissingRouteError,
    ServiceMediator,
)
from app.settings import Settings


def test_mediator_dispatches_async_handler_and_returns_result() -> None:
    mediator = ServiceMediator()

    async def handler(payload: dict[str, int]) -> dict[str, int]:
        return {"total": payload["left"] + payload["right"]}

    mediator.register("numbers.add", handler)

    result = asyncio.run(mediator.request("numbers.add", {"left": 2, "right": 3}))

    assert result == {"total": 5}


def test_mediator_rejects_duplicate_route_registration() -> None:
    mediator = ServiceMediator()

    async def handler(payload: object) -> object:
        return payload

    mediator.register("users.lookup", handler)

    try:
        mediator.register("users.lookup", handler)
    except DuplicateRouteError as error:
        assert error.detail == "Orchestration route already registered: users.lookup"
    else:
        raise AssertionError("duplicate route registration should fail")


def test_mediator_reports_missing_route_as_typed_error() -> None:
    mediator = ServiceMediator()

    try:
        asyncio.run(mediator.request("users.lookup", {"id": "missing"}))
    except MissingRouteError as error:
        assert error.detail == "Orchestration route not registered: users.lookup"
    else:
        raise AssertionError("missing route request should fail")


def test_domain_errors_are_mapped_to_detail_json_and_status_codes() -> None:
    application = create_app()
    request = object()

    cases = (
        (NotFoundError("record missing"), 404),
        (ConflictError("record exists"), 409),
        (ForbiddenError("role denied"), 403),
        (AppError("invalid operation"), 400),
    )

    for error, expected_status in cases:
        response = asyncio.run(application.exception_handlers[type(error)](request, error))
        assert isinstance(response, JSONResponse)
        assert response.status_code == expected_status
        assert json.loads(response.body) == {"detail": error.detail}


def test_settings_have_development_safe_defaults() -> None:
    settings = Settings()

    assert settings.jwt_secret == "development-secret-change-me"
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_minutes == 60
    assert settings.upload_root == "/data/uploads"
    assert settings.max_upload_bytes == 10 * 1024 * 1024
    assert settings.app_timezone == "Asia/Kolkata"


def test_compose_declares_healthcheck_database_urls_and_upload_volume() -> None:
    compose = (Path(__file__).resolve().parents[3] / "docker-compose.yml").read_text()

    backend_block = compose.split("\n  backend:\n", 1)[1].split("\n  frontend:\n", 1)[0]
    migration_block = compose.split("\n  database-migration:\n", 1)[1].split("\n  backend:\n", 1)[0]
    assert "/api/v1/health" in backend_block
    assert "env_file:" in backend_block
    assert "./backend/app/.env" in backend_block
    assert "env_file:" in migration_block
    assert "./backend/database/.env" in migration_block
    assert "uploads_data:/data/uploads" in backend_block


def test_error_handlers_are_registered_on_fastapi_application() -> None:
    application = create_app()

    assert isinstance(application, FastAPI)
    assert NotFoundError in application.exception_handlers
    assert ConflictError in application.exception_handlers
    assert ForbiddenError in application.exception_handlers
    assert AppError in application.exception_handlers
