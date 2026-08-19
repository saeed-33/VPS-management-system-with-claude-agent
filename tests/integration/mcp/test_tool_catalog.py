"""Tests for test tool catalog.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.interfaces.mcp، app.interfaces.mcp.catalog.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from app.interfaces.mcp.registry import ProjectMcpToolBoundary
from app.interfaces.mcp.catalog import (
    PROJECT_TOOL_GROUPS,
    tool_group_for,
)

from tests.integration.mcp.test_tool_boundary import (
    MonitoringService,
    ProfileService,
    ReportService,
    ServerService,
)


def boundary():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى boundary؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return ProjectMcpToolBoundary(
        server_service=ServerService(),
        monitoring_profile_service=ProfileService(),
        monitoring_service=MonitoringService(),
        report_query_service=ReportService(),
    )


def test_every_project_tool_belongs_to_one_group():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_every_project_tool_belongs_to_one_group؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    tool_ids = {
        tool.tool_id
        for tool in boundary().list_tools()
    }
    grouped_ids = [
        tool_id
        for group in PROJECT_TOOL_GROUPS
        for tool_id in group.tool_ids
    ]

    assert set(grouped_ids) == tool_ids
    assert len(grouped_ids) == len(
        set(grouped_ids)
    )


def test_boundary_exposes_grouped_tool_definitions():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_boundary_exposes_grouped_tool_definitions؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    grouped = boundary().list_tool_groups()

    assert [
        tool.tool_id
        for tool in grouped["monitoring"]
    ] == [
        "get_server_context",
        "get_monitoring_profile",
        "run_monitoring",
    ]
    assert [
        tool.tool_id
        for tool in grouped["remediation"]
    ] == [
        "propose_remediation",
        "create_remediation_plan",
        "test_remediation_in_sandbox",
        "get_sandbox_result",
        "request_user_approval",
        "apply_approved_remediation",
        "attempt_autonomous_remediation",
    ]


def test_tool_group_lookup_rejects_unknown_tools():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_tool_group_lookup_rejects_unknown_tools؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert (
        tool_group_for("search_knowledge")
        == "retrieval"
    )

    try:
        tool_group_for("raw_ssh")
    except KeyError as exc:
        assert "raw_ssh" in str(exc)
    else:
        raise AssertionError(
            "Unknown tool was assigned a group."
        )
