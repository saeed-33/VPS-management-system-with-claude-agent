"""
حد MCP يكشف Project capabilities لـClaude عبر أدوات typed ومتحقق منها.

الموقع في المعمارية: MCP capability boundary.
يُستدعى بواسطة: Claude أو خادم MCP.
يعتمد مباشرة على: app.interfaces.mcp.registry، app.interfaces.mcp.schemas.
الحد المعماري: MCP exposure ليس enforcement أمنيًا مستقلًا؛ التحقق الفعلي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
