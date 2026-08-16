"""
واجهة MCP الخاصة بالمشروع.

تجمع حدود الأدوات ومخططاتها ومسلسلاتها وخادم البروتوكول، بحيث تصل الأدوات
الخارجية إلى خدمات التطبيق عبر أسماء وعقود محددة قابلة للتدقيق.
"""
from __future__ import annotations

from app.interfaces.mcp.registry import ProjectMcpToolBoundary
from app.interfaces.mcp.schemas import (
    ProjectToolCall,
    ProjectToolDefinition,
    ProjectToolResult,
)

__all__ = [
    "ProjectMcpToolBoundary",
    "ProjectToolCall",
    "ProjectToolDefinition",
    "ProjectToolResult",
]
