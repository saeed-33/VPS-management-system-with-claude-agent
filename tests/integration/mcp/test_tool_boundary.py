"""Tests for test tool boundary.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.interfaces.mcp، app.core.contracts.reports.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

from app.interfaces.mcp.registry import ProjectMcpToolBoundary
from app.interfaces.mcp.schemas.call import ProjectToolCall
from app.core.contracts.reports.monitoring_report_data import MonitoringReportData
from app.core.contracts.reports.monitoring_report_status import MonitoringReportStatus
from app.core.contracts.reports.report_details_dto import ReportDetailsDTO
from app.core.contracts.reports.report_list_item_dto import ReportListItemDTO


NOW = datetime(
    2026,
    8,
    11,
    tzinfo=timezone.utc,
)


@dataclass
class Server:
    """
    يمثل Server جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    id: int = 1
    name: str = "server-1"
    host: str = "10.0.0.1"
    port: int = 22
    username: str = "root"
    description: str | None = None
    monitor_enabled: bool = True
    interval_seconds: int = 60
    monitoring_profile_id: int | None = 5
    status: str = "unknown"
    last_checked_at = None
    last_success_at = None
    last_error = None
    last_report_id: int | None = 10


@dataclass
class Profile:
    """
    يمثل Profile جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    id: int = 5
    name: str = "baseline"
    description: str | None = None
    enabled: bool = True


@dataclass
class Command:
    """
    يمثل Command جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    id: int = 9
    name: str = "uptime"
    command: str = "uptime"
    timeout_seconds: float = 10.0


@dataclass
class Assignment:
    """
    يمثل Assignment جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    execution_order: int = 1
    enabled: bool = True
    custom_timeout_seconds: float | None = None


class ServerService:
    """
    يمثل ServerService جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def get_server(
        self,
        server_id,
    ):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_server؛ المدخلات المهمة: server_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        assert server_id == 1
        return Server()


class ProfileService:
    """
    يمثل ProfileService جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def get_profile(
        self,
        profile_id,
    ):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_profile؛ المدخلات المهمة: profile_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        assert profile_id == 5
        return Profile()

    def list_profile_commands(
        self,
        profile_id,
    ):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_profile_commands؛ المدخلات المهمة: profile_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        assert profile_id == 5
        return [
            (
                Command(),
                Assignment(),
            )
        ]


class MonitoringService:
    """
    يمثل MonitoringService جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.ran_server_ids = []

    async def run(
        self,
        server_id,
    ):
        """
        يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى run؛ المدخلات المهمة: server_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.ran_server_ids.append(
            server_id
        )
        return MonitoringReportData(
            server_id=server_id,
            status=(
                MonitoringReportStatus.SUCCESS
            ),
            started_at=NOW,
            finished_at=NOW,
            duration_ms=12.5,
            connection_successful=True,
            error_message=None,
            commands_total=1,
            commands_succeeded=1,
            commands_failed=0,
        )


class ReportService:
    """
    يمثل ReportService جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.reports = {
            10: ReportDetailsDTO(
                id=10,
                server_id=1,
                monitoring_profile_id=5,
                server_name="server-1",
                server_host="10.0.0.1",
                status="success",
                started_at=NOW,
                finished_at=NOW,
                duration_ms=12.5,
                connection_successful=True,
                error_message=None,
                commands_total=1,
                commands_succeeded=1,
                commands_failed=0,
            )
        }

    def list_reports(
        self,
        *,
        server_id=None,
        status=None,
        page=1,
        page_size=50,
    ):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_reports؛ المدخلات المهمة: server_id، status، page، page_size.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        assert server_id == 1
        assert page == 1
        assert page_size == 1
        return [
            ReportListItemDTO(
                id=10,
                server_id=1,
                server_name="server-1",
                status="success",
                started_at=NOW,
                finished_at=NOW,
                duration_ms=12.5,
                connection_successful=True,
                commands_total=1,
                commands_succeeded=1,
                commands_failed=0,
            )
        ], 1

    def get_report(
        self,
        report_id,
    ):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_report؛ المدخلات المهمة: report_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.reports[report_id]


def boundary(
    report_service=None,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى boundary؛ المدخلات المهمة: report_service.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return ProjectMcpToolBoundary(
        server_service=ServerService(),
        monitoring_profile_service=(
            ProfileService()
        ),
        monitoring_service=MonitoringService(),
        report_query_service=(
            report_service
            if report_service is not None
            else ReportService()
        ),
    )


def run_tool(
    tool_id,
    arguments,
    *,
    tool_boundary=None,
):
    """
    ينفذ مرحلة الأداة أو يحفظ نتيجة التقييم ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى run_tool؛ المدخلات المهمة: tool_id، arguments، tool_boundary.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return asyncio.run(
        (
            tool_boundary
            if tool_boundary is not None
            else boundary()
        ).execute(
            ProjectToolCall(
                tool_id=tool_id,
                arguments=arguments,
            )
        )
    )


def test_tool_inventory_is_deliberately_small():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_tool_inventory_is_deliberately_small؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    tool_ids = [
        tool.tool_id
        for tool in boundary().list_tools()
    ]

    assert tool_ids == [
        "analyze_report",
        "apply_approved_remediation",
        "attempt_autonomous_remediation",
        "create_remediation_plan",
        "find_exact_report_match",
        "get_analysis",
        "get_available_specialists",
        "get_evidence",
        "get_investigation",
        "get_investigation_status",
        "get_latest_report",
        "get_monitoring_profile",
        "get_report",
        "get_sandbox_result",
        "get_server_context",
        "get_specialist_definition",
        "get_top_similar_reports",
        "propose_remediation",
        "request_user_approval",
        "run_monitoring",
        "run_specialist",
        "search_knowledge",
        "search_similar_incidents",
        "start_investigation",
        "test_remediation_in_sandbox",
    ]

    read_modes = {
        tool.tool_id: tool.read_only
        for tool in boundary().list_tools()
    }
    assert read_modes["start_investigation"] is False
    assert read_modes["run_specialist"] is False
    assert read_modes["create_remediation_plan"] is False
    assert read_modes["test_remediation_in_sandbox"] is False
    assert read_modes["request_user_approval"] is False
    assert read_modes["apply_approved_remediation"] is False
    assert read_modes["attempt_autonomous_remediation"] is False
    assert all(
        read_only
        for tool_id, read_only in read_modes.items()
        if tool_id not in {
            "start_investigation",
            "run_specialist",
            "create_remediation_plan",
            "test_remediation_in_sandbox",
            "request_user_approval",
            "apply_approved_remediation",
            "attempt_autonomous_remediation",
        }
    )


def test_get_server_context_uses_project_service():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_get_server_context_uses_project_service؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = run_tool(
        "get_server_context",
        {
            "server_id": 1,
        },
    )

    assert result.success is True
    assert result.data["server"]["id"] == 1
    assert (
        result.data["server"][
            "monitoring_profile_id"
        ]
        == 5
    )


def test_get_monitoring_profile_includes_commands():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_get_monitoring_profile_includes_commands؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = run_tool(
        "get_monitoring_profile",
        {
            "profile_id": 5,
        },
    )

    assert result.success is True
    profile = result.data["profile"]
    assert profile["id"] == 5
    assert profile["commands"][0]["name"] == "uptime"
    assert (
        profile["commands"][0][
            "execution_order"
        ]
        == 1
    )


def test_run_monitoring_invokes_existing_service_and_reads_report():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_run_monitoring_invokes_existing_service_and_reads_report؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = run_tool(
        "run_monitoring",
        {
            "server_id": 1,
        },
    )

    assert result.success is True
    assert (
        result.data["monitoring_report"]["status"]
        == "success"
    )
    assert (
        result.data["persisted_report"]["id"]
        == 10
    )


def test_get_report_reads_persisted_report():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_get_report_reads_persisted_report؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = run_tool(
        "get_report",
        {
            "report_id": 10,
        },
    )

    assert result.success is True
    assert result.data["report"]["id"] == 10


def test_get_latest_report_returns_controlled_not_found():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_get_latest_report_returns_controlled_not_found؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    class EmptyReportService(ReportService):
        """
        يمثل EmptyReportService جزءًا من طبقة Test suite.

        يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
        تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
        """
        def list_reports(
            self,
            **kwargs,
        ):
            """
            يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

            تُستدعى عندما يصل المسار إلى list_reports؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
            تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
            """
            return [], 0

    result = run_tool(
        "get_latest_report",
        {
            "server_id": 1,
        },
        tool_boundary=boundary(
            EmptyReportService()
        ),
    )

    assert result.success is False
    assert result.error_code == "report_not_found"


def test_invalid_input_is_normalized():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_invalid_input_is_normalized؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = run_tool(
        "get_server_context",
        {
            "server_id": "1",
        },
    )

    assert result.success is False
    assert result.error_code == "validation_error"


def test_unknown_tool_is_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_unknown_tool_is_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = run_tool(
        "raw_ssh",
        {
            "command": "uptime",
        },
    )

    assert result.success is False
    assert result.error_code == "unknown_tool"
