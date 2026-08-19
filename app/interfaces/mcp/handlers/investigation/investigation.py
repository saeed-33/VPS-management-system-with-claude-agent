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

from .investigation_lookup import _InvestigationLookupHelpers
from .lifecycle import _InvestigationLifecycleOperations
from .specialist_execution import _SpecialistExecutionOperations
from .specialists import _InvestigationSpecialistOperations


class InvestigationToolsMixin(_InvestigationLifecycleOperations, _InvestigationSpecialistOperations, _SpecialistExecutionOperations, _InvestigationLookupHelpers):
    """
    يوفر معالجات دورة التحقيق والاختصاصيين والأدلة.
    """
