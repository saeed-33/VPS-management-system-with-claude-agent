from app.interfaces.mcp import ProjectMcpToolBoundary
from app.interfaces.mcp.catalog import (
    PROJECT_TOOL_GROUPS,
    tool_group_for,
)

from tests.test_project_mcp_tool_boundary import (
    MonitoringService,
    ProfileService,
    ReportService,
    ServerService,
)


def boundary():
    return ProjectMcpToolBoundary(
        server_service=ServerService(),
        monitoring_profile_service=ProfileService(),
        monitoring_service=MonitoringService(),
        report_query_service=ReportService(),
    )


def test_every_project_tool_belongs_to_one_group():
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
    ]


def test_tool_group_lookup_rejects_unknown_tools():
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
