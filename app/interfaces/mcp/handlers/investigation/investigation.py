"""
معالجات أدوات التحقيق في MCP.

تبدأ التحقيق وتقرأ حالته وأدلته واختصاصييه، وتنفذ اختصاصيًا أو تعرض تقدمه
مع إبقاء دورة التحقيق داخل خدمات المجال.
"""
from __future__ import annotations

from typing import Any

from app.core.contracts.investigation.investigation_budget import InvestigationBudget
from app.core.contracts.investigation.specialist_task import SpecialistTask
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus
from app.interfaces.mcp.schemas.result import ProjectToolResult
from app.interfaces.mcp.serializers import (
    serialize_specialist_definition,
    serialize_specialist_loop_result,
    serialize_value,
)

from .operations_1 import _InvestigationToolsOperations1
from .operations_2 import _InvestigationToolsOperations2
from .operations_3 import _InvestigationToolsOperations3
from .operations_4 import _InvestigationToolsOperations4


class InvestigationToolsMixin(_InvestigationToolsOperations1, _InvestigationToolsOperations2, _InvestigationToolsOperations3, _InvestigationToolsOperations4):
    """
    يوفر معالجات دورة التحقيق والاختصاصيين والأدلة.
    """
