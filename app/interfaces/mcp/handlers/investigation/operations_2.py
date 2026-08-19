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


class _InvestigationToolsOperations2:
    """ينظم مجموعة من عمليات التحقيق في MCP."""

    async def _get_evidence(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        يعيد الأدلة المجموعة للتحقيق وفق المرشحات المطلوبة.
        """
        detail = self._read_investigation(
            arguments
        )

        if detail is None:
            return ProjectToolResult(
                tool_id="get_evidence",
                success=False,
                error_code="investigation_not_found",
                error_message="Investigation not found.",
            )

        evidence = (
            detail.runtime.evidence
            if (
                detail.runtime is not None
                and detail.runtime.evidence
            )
            else ()
        )

        return ProjectToolResult(
            tool_id="get_evidence",
            success=True,
            data={
                "investigation_id": (
                    detail.investigation_id
                ),
                "evidence": serialize_value(
                    evidence
                ),
            },
        )

    async def _get_available_specialists(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        يعرض الاختصاصيين المتاحين للمشاركة في التحقيق.
        """
        self._require_dependency(
            self._specialist_registry,
            "specialist_registry",
        )

        domains = arguments.get("domains", [])
        if not isinstance(domains, list):
            raise ValueError(
                "domains must be a list."
            )

        snapshot = (
            self._specialist_registry.snapshot()
        )

        if domains:
            definitions = tuple(
                match.specialist
                for match in snapshot.find_by_domains(
                    domains
                )
            )
        else:
            definitions = snapshot.definitions

        return ProjectToolResult(
            tool_id="get_available_specialists",
            success=True,
            data={
                "specialists": [
                    serialize_specialist_definition(
                        item
                    )
                    for item in definitions
                ],
            },
        )

    async def _get_specialist_definition(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        يجلب تعريف اختصاصي محدد للعرض أو الاختيار.
        """
        specialist = self._specialist_by_slug(
            arguments
        )

        if specialist is None:
            return ProjectToolResult(
                tool_id="get_specialist_definition",
                success=False,
                error_code="specialist_not_found",
                error_message=(
                    "Enabled Specialist definition "
                    "was not found."
                ),
            )

        return ProjectToolResult(
            tool_id="get_specialist_definition",
            success=True,
            data={
                "specialist": (
                    serialize_specialist_definition(
                        specialist
                    )
                )
            },
        )
