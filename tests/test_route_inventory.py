from tools.list_routes import (
    collect_routes,
)


def test_route_inventory_contains_application_routes(
) -> None:
    routes = collect_routes()

    paths = {
        item["path"]
        for item in routes
    }

    expected = {
        "/",
        "/servers",
        "/commands",
        "/monitoring-profiles",
        "/reports",
        "/reports/{report_id}",
        "/specialists",
        "/api/servers",
        "/api/commands",
        "/api/monitoring-profiles",
        "/api/reports",
        "/api/specialists",
        "/health",
    }

    missing = expected - paths

    assert not missing, (
        "Effective FastAPI route inventory "
        "is missing registered paths: "
        + ", ".join(
            sorted(missing)
        )
    )


def test_web_routes_are_excluded_from_openapi(
) -> None:
    routes = collect_routes()

    web_paths = {
        "/",
        "/servers",
        "/commands",
        "/monitoring-profiles",
        "/reports",
        "/reports/{report_id}",
        "/specialists",
    }

    found = {
        item["path"]: item
        for item in routes
        if item["path"] in web_paths
    }

    assert set(found) == web_paths

    assert all(
        not item["include_in_schema"]
        for item in found.values()
    )


def test_specialists_api_is_in_openapi_inventory(
) -> None:
    routes = collect_routes()

    specialist_routes = [
        item
        for item in routes
        if item["path"].startswith(
            "/api/specialists"
        )
    ]

    assert specialist_routes

    assert all(
        item["include_in_schema"]
        for item in specialist_routes
    )


def test_health_route_remains_visible(
) -> None:
    routes = collect_routes()

    health = [
        item
        for item in routes
        if item["path"] == "/health"
    ]

    assert len(health) == 1
    assert health[0]["include_in_schema"] is True
