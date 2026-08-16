"""
حد MCP يكشف Project capabilities لـClaude عبر أدوات typed ومتحقق منها.

الموقع في المعمارية: MCP capability boundary.
يُستدعى بواسطة: Claude أو خادم MCP.
يعتمد مباشرة على: app.interfaces.mcp.handlers.analysis، app.interfaces.mcp.handlers.common، app.interfaces.mcp.handlers.definitions، app.interfaces.mcp.handlers.investigation، app.interfaces.mcp.handlers.monitoring، app.interfaces.mcp.handlers.remediation.
الحد المعماري: MCP exposure ليس enforcement أمنيًا مستقلًا؛ التحقق الفعلي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from app.interfaces.mcp.handlers.analysis import AnalysisToolsMixin
from app.interfaces.mcp.handlers.common import BoundaryCommonMixin
from app.interfaces.mcp.handlers.definitions import BoundaryDefinitionsMixin
from app.interfaces.mcp.handlers.investigation import InvestigationToolsMixin
from app.interfaces.mcp.handlers.monitoring import MonitoringToolsMixin
from app.interfaces.mcp.handlers.remediation import RemediationToolsMixin

__all__ = [
    "AnalysisToolsMixin",
    "BoundaryCommonMixin",
    "BoundaryDefinitionsMixin",
    "InvestigationToolsMixin",
    "MonitoringToolsMixin",
    "RemediationToolsMixin",
]
