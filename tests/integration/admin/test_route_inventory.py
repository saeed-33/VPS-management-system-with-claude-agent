"""Tests for test route inventory.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from tools.dev.list_routes import (
    collect_routes,
)


def test_route_inventory_contains_application_routes(
) -> None:
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_route_inventory_contains_application_routes؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
        "/knowledge-sources",
        "/system",
        "/api/servers",
        "/api/commands",
        "/api/monitoring-profiles",
        "/api/reports",
        "/api/specialists",
        "/api/diagnostic-tools",
        "/api/system/runtime",
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_web_routes_are_excluded_from_openapi؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    routes = collect_routes()

    web_paths = {
        "/",
        "/servers",
        "/commands",
        "/monitoring-profiles",
        "/reports",
        "/reports/{report_id}",
        "/specialists",
        "/system",
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_specialists_api_is_in_openapi_inventory؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_health_route_remains_visible؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    routes = collect_routes()

    health = [
        item
        for item in routes
        if item["path"] == "/health"
    ]

    assert len(health) == 1
    assert health[0]["include_in_schema"] is True
