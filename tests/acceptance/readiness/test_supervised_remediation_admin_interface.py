"""Tests for test supervised remediation admin interface.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.main.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from pathlib import Path

from app.main import app


def test_phase5_admin_routes_are_registered():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_phase5_admin_routes_are_registered؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    def collect(routes):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى collect؛ المدخلات المهمة: routes.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_phase5_admin_page_is_operator_review_surface؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    template = Path("app/interfaces/admin/web/templates/remediation.html").read_text(encoding="utf-8")
    assert "Approve exact plan" in template
    assert "HIGH/CRITICAL" in template
    assert "/api/remediation/" in template
