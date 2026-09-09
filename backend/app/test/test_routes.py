from app.main import create_app


def test_health_route_uses_versioned_api_prefix() -> None:
    routes = {route.path for route in create_app().routes}

    assert "/api/v1/health" in routes
    assert "/api/v1/queries" in routes
    assert "/api/v1/product-lineups" in routes
    assert "/api/v1/assignments" in routes
    assert "/api/v1/assignments/{assignment_id}" in routes
    assert "/health" not in routes
