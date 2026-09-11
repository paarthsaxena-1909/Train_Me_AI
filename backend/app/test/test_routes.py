import asyncio

import httpx

from app.main import create_app


def test_health_route_uses_versioned_api_prefix() -> None:
    routes = {route.path for route in create_app().routes}

    assert "/api/v1/health" in routes
    assert "/api/v1/queries" in routes
    assert "/api/v1/product-lineups" in routes
    assert "/api/v1/assignments" in routes
    assert "/api/v1/assignments/{assignment_id}" in routes
    assert "/health" not in routes


def test_rejected_cors_preflight_logs_the_origin_and_reason(capsys) -> None:
    async def send_preflight() -> httpx.Response:
        transport = httpx.ASGITransport(app=create_app())
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.options(
                "/api/v1/auth/agents/login",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type",
                },
            )

    response = asyncio.run(send_preflight())
    captured = capsys.readouterr().out

    assert response.status_code == 400
    assert "cors preflight rejected" in captured
    assert "reason=origin_not_allowed" in captured
    assert "origin=http://localhost:3000" in captured
    assert "allowed_origins=http://localhost:5173" in captured
    assert "token" not in captured.lower()
