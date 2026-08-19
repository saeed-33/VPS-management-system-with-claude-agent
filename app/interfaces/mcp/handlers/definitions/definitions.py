"""واجهة تجميع تعريفات أدوات MCP."""
from __future__ import annotations

from app.interfaces.mcp.schemas.definition import ProjectToolDefinition

from .investigation import build_investigation_definitions
from .read import build_read_definitions
from .remediation import build_remediation_definitions


class BoundaryDefinitionsMixin:
    """يوفر تعريفات الأدوات وأشكالها لحد MCP."""

    @staticmethod
    def _build_definitions() -> list[ProjectToolDefinition]:
        """يبني تعريفات الأدوات من مجموعات المجال."""
        return [
            *build_read_definitions(),
            *build_investigation_definitions(),
            *build_remediation_definitions(),
        ]
