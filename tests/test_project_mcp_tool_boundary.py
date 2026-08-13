import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

from app.interfaces.mcp import (
    ProjectMcpToolBoundary,
    ProjectToolCall,
)
from app.core.contracts.reports import (
    MonitoringReportData,
    MonitoringReportStatus,
    ReportDetailsDTO,
    ReportListItemDTO,
)


NOW = datetime(
    2026,
    8,
    11,
    tzinfo=timezone.utc,
)


@dataclass
class Server:
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
    id: int = 5
    name: str = "baseline"
    description: str | None = None
    enabled: bool = True


@dataclass
class Command:
    id: int = 9
    name: str = "uptime"
    command: str = "uptime"
    timeout_seconds: float = 10.0


@dataclass
class Assignment:
    execution_order: int = 1
    enabled: bool = True
    custom_timeout_seconds: float | None = None


class ServerService:
    def get_server(
        self,
        server_id,
    ):
        assert server_id == 1
        return Server()


class ProfileService:
    def get_profile(
        self,
        profile_id,
    ):
        assert profile_id == 5
        return Profile()

    def list_profile_commands(
        self,
        profile_id,
    ):
        assert profile_id == 5
        return [
            (
                Command(),
                Assignment(),
            )
        ]


class MonitoringService:
    def __init__(self):
        self.ran_server_ids = []

    async def run(
        self,
        server_id,
    ):
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
    def __init__(self):
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
        return self.reports[report_id]


def boundary(
    report_service=None,
):
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
    tool_ids = [
        tool.tool_id
        for tool in boundary().list_tools()
    ]

    assert tool_ids == [
        "analyze_report",
        "apply_approved_remediation",
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
        }
    )


def test_get_server_context_uses_project_service():
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
    result = run_tool(
        "get_report",
        {
            "report_id": 10,
        },
    )

    assert result.success is True
    assert result.data["report"]["id"] == 10


def test_get_latest_report_returns_controlled_not_found():
    class EmptyReportService(ReportService):
        def list_reports(
            self,
            **kwargs,
        ):
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
    result = run_tool(
        "get_server_context",
        {
            "server_id": "1",
        },
    )

    assert result.success is False
    assert result.error_code == "validation_error"


def test_unknown_tool_is_rejected():
    result = run_tool(
        "raw_ssh",
        {
            "command": "uptime",
        },
    )

    assert result.success is False
    assert result.error_code == "unknown_tool"
