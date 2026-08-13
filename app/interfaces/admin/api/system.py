from fastapi import APIRouter, Depends

from app.interfaces.admin.dependencies import (
    get_claude_supervisor,
    get_project_tool_boundary,
)
from app.runtime.claude.supervisor import (
    ClaudeSupervisor,
)
from app.interfaces.mcp.registry import (
    ProjectMcpToolBoundary,
)
from app.core.config import settings


router = APIRouter(
    tags=["system"],
)


@router.get(
    "/api/system/runtime",
)
async def get_runtime_overview(
    supervisor: ClaudeSupervisor = Depends(
        get_claude_supervisor
    ),
    tool_boundary: ProjectMcpToolBoundary = Depends(
        get_project_tool_boundary
    ),
) -> dict:
    tool_groups = (
        tool_boundary.list_tool_groups()
    )

    serialized_groups = [
        {
            "name": name,
            "tool_count": len(tools),
            "tools": [
                {
                    "tool_id": tool.tool_id,
                    "description": (
                        tool.description
                    ),
                    "read_only": tool.read_only,
                    "input_schema": (
                        tool.input_schema
                    ),
                }
                for tool in tools
            ],
        }
        for name, tools in tool_groups.items()
    ]

    return {
        "supervisor": supervisor.status,
        "claude_runtime": {
            "enabled": settings.claude_runtime_enabled,
            "executable": settings.claude_runtime_executable,
            "model": settings.effective_claude_runtime_model,
            "agent": settings.claude_runtime_agent,
            "max_turns": settings.claude_runtime_max_turns,
        },
        "ollama": {
            "provider": settings.llm_provider,
            "enabled": settings.llm_enabled,
            "base_url": settings.ollama_base_url,
            "model": settings.ollama_model,
        },
        "mcp": {
            "server_name": "vps",
            "configured": bool(serialized_groups),
            "tool_count": sum(
                group["tool_count"]
                for group in serialized_groups
            ),
        },
        "scheduler": {
            "state": supervisor.status.get(
                "state",
                "unknown",
            ),
            "polling_interval_seconds": (
                settings.monitor_polling_interval_seconds
            ),
        },
        "tool_count": sum(
            group["tool_count"]
            for group in serialized_groups
        ),
        "tool_groups": serialized_groups,
    }
