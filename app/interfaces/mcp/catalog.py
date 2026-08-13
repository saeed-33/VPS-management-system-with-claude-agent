from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.interfaces.mcp.schemas import ProjectToolDefinition


@dataclass(slots=True, frozen=True)
class ProjectToolGroup:
    name: str
    tool_ids: tuple[str, ...]


PROJECT_TOOL_GROUPS = (
    ProjectToolGroup(
        name="monitoring",
        tool_ids=(
            "get_server_context",
            "get_monitoring_profile",
            "run_monitoring",
        ),
    ),
    ProjectToolGroup(
        name="reports",
        tool_ids=(
            "get_report",
            "get_latest_report",
        ),
    ),
    ProjectToolGroup(
        name="retrieval",
        tool_ids=(
            "find_exact_report_match",
            "search_similar_incidents",
            "get_top_similar_reports",
            "analyze_report",
            "get_analysis",
            "search_knowledge",
        ),
    ),
    ProjectToolGroup(
        name="investigation",
        tool_ids=(
            "start_investigation",
            "get_investigation",
            "get_investigation_status",
            "get_evidence",
        ),
    ),
    ProjectToolGroup(
        name="specialists",
        tool_ids=(
            "get_available_specialists",
            "get_specialist_definition",
            "run_specialist",
        ),
    ),
    ProjectToolGroup(
        name="remediation",
        tool_ids=(
            "propose_remediation",
            "create_remediation_plan",
            "test_remediation_in_sandbox",
            "get_sandbox_result",
            "request_user_approval",
            "apply_approved_remediation",
        ),
    ),
)


def tool_group_for(
    tool_id: str,
) -> str:
    for group in PROJECT_TOOL_GROUPS:
        if tool_id in group.tool_ids:
            return group.name

    raise KeyError(
        f"Unknown project tool group for {tool_id}."
    )


def group_definitions(
    definitions: list[ProjectToolDefinition],
) -> dict[str, list[ProjectToolDefinition]]:
    by_id = {
        item.tool_id: item
        for item in definitions
    }
    grouped: dict[str, list[ProjectToolDefinition]] = {}

    for group in PROJECT_TOOL_GROUPS:
        grouped[group.name] = [
            by_id[tool_id]
            for tool_id in group.tool_ids
            if tool_id in by_id
        ]

    return grouped
