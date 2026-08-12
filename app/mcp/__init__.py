from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.mcp.schemas import (
    ProjectToolCall,
    ProjectToolDefinition,
    ProjectToolResult,
)

if TYPE_CHECKING:
    from app.tools.project_boundary import (
        ProjectMcpToolBoundary,
    )


__all__ = [
    "ProjectMcpToolBoundary",
    "ProjectToolCall",
    "ProjectToolDefinition",
    "ProjectToolResult",
]


def __getattr__(
    name: str,
) -> Any:
    if name == "ProjectMcpToolBoundary":
        from app.tools.project_boundary import (
            ProjectMcpToolBoundary,
        )

        return ProjectMcpToolBoundary

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )
