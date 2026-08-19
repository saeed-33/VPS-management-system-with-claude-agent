"""Tests for test diagnostic tools api.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.interfaces.admin.api.diagnostic_tools.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interfaces.admin.api.diagnostic_tools import router


def test_diagnostic_tools_api_lists_registry():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_diagnostic_tools_api_lists_registry؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    app = FastAPI()
    app.include_router(router)

    response = TestClient(app).get(
        "/api/diagnostic-tools"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload

    by_id = {
        item["tool_id"]: item
        for item in payload
    }

    assert "systemd-status" in by_id
    assert "network-listeners" in by_id
    assert "nginx-config-test" in by_id

    assert (
        by_id["systemd-status"]["risk"]
        == "read_only"
    )
