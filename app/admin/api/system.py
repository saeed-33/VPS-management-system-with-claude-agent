from fastapi import APIRouter, Depends

from app.admin.dependencies import (
    get_claude_supervisor,
    get_project_tool_boundary,
)
from app.runtime.claude.supervisor import (
    ClaudeSupervisor,
)
from app.tools.project_boundary import (
    ProjectMcpToolBoundary,
)


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
        "tool_count": sum(
            group["tool_count"]
            for group in serialized_groups
        ),
        "tool_groups": serialized_groups,
    }
