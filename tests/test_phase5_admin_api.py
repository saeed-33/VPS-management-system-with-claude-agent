from pathlib import Path

from app.main import app


def test_phase5_admin_routes_are_registered():
    def collect(routes):
        paths = set()
        for route in routes:
            if hasattr(route, "path"):
                paths.add(route.path)
            if hasattr(route, "routes"):
                paths.update(collect(route.routes))
            if hasattr(route, "original_router"):
                paths.update(collect(route.original_router.routes))
        return paths

    paths = collect(app.routes)
    assert "/api/remediation" in paths
    assert "/api/remediation/{plan_id}" in paths
    assert "/api/remediation/{plan_id}/audit" in paths
    assert "/api/remediation/{plan_id}/execute" in paths
    assert "/api/remediation/{plan_id}/rollback" in paths
    assert "/api/remediation/{plan_id}/sandbox-validation" in paths


def test_phase5_admin_page_is_operator_review_surface():
    template = Path("app/interfaces/admin/web/templates/remediation.html").read_text(encoding="utf-8")
    assert "Approve exact plan" in template
    assert "HIGH/CRITICAL" in template
    assert "/api/remediation/" in template
