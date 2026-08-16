"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.interfaces.admin.api.system، app.interfaces.admin.dependencies، app.interfaces.mcp.schemas.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interfaces.admin.api.system import router
from app.interfaces.admin.dependencies import (
    get_claude_supervisor,
    get_project_tool_boundary,
)
from app.interfaces.mcp.schemas import ProjectToolDefinition


class FakeSupervisor:
    """
    يمثل FakeSupervisor جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    @property
    def status(self) -> dict:
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى status؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد dict أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return {
            "runtime": "claude",
            "state": "active",
        }


class FakeToolBoundary:
    """
    يمثل FakeToolBoundary جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def list_tool_groups(
        self,
    ) -> dict[str, list[ProjectToolDefinition]]:
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_tool_groups؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد dict[str, list[ProjectToolDefinition]] أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return {
            "monitoring": [
                ProjectToolDefinition(
                    tool_id="run_monitoring",
                    description="Run monitoring.",
                    input_schema={
                        "type": "object",
                    },
                    read_only=False,
                )
            ],
            "reports": [
                ProjectToolDefinition(
                    tool_id="get_report",
                    description="Read report.",
                    input_schema={
                        "type": "object",
                    },
                    read_only=True,
                )
            ],
        }


def test_system_runtime_api_exposes_supervisor_and_tools():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_system_runtime_api_exposes_supervisor_and_tools؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[
        get_claude_supervisor
    ] = FakeSupervisor
    app.dependency_overrides[
        get_project_tool_boundary
    ] = FakeToolBoundary

    response = TestClient(app).get(
        "/api/system/runtime"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["supervisor"] == {
        "runtime": "claude",
        "state": "active",
    }
    assert payload["tool_count"] == 2
    assert [
        group["name"]
        for group in payload["tool_groups"]
    ] == [
        "monitoring",
        "reports",
    ]
    assert (
        payload["tool_groups"][0]["tools"][0][
            "read_only"
        ]
        is False
    )
