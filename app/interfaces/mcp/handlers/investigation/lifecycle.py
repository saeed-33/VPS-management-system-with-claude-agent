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


class _InvestigationLifecycleOperations:
    """ينظم مجموعة من عمليات التحقيق في MCP."""

    async def _start_investigation(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        ينشئ تحقيقًا جديدًا من التقرير والسيرفر والسياق المطلوب.
        """
        self._require_dependency(
            self._investigation_router,
            "investigation_router",
        )
        self._require_dependency(
            self._investigation_persistence_service,
            "investigation_persistence_service",
        )
        self._require_dependency(
            self._investigation_read_service,
            "investigation_read_service",
        )
        self._require_dependency(
            self._analysis_repository,
            "analysis_repository",
        )

        report_id = self._required_int(
            arguments,
            "report_id",
        )
        analysis_id = arguments.get(
            "analysis_id"
        )
        if analysis_id is not None and not isinstance(
            analysis_id,
            int,
        ):
            raise ValueError(
                "analysis_id must be an integer."
            )

        report = (
            self._report_query_service
            .get_report(report_id)
        )

        analysis = (
            self._analysis_repository.get_by_id(
                analysis_id
            )
            if analysis_id is not None
            else self._analysis_repository
            .get_by_report_id(report_id)
        )

        if analysis is None:
            return ProjectToolResult(
                tool_id="start_investigation",
                success=False,
                error_code="analysis_not_found",
                error_message=(
                    "Analysis is required before "
                    "starting investigation."
                ),
            )

        decision = (
            self._investigation_router
            .route(
                report=report,
                analysis=analysis,
            )
        )

        model = (
            self
            ._investigation_persistence_service
            .persist_routing_decision(
                server_id=report.server_id,
                report_id=report_id,
                analysis_id=analysis.id,
                decision=decision,
            )
        )

        detail = (
            self._investigation_read_service
            .get(model.investigation_id)
        )

        return ProjectToolResult(
            tool_id="start_investigation",
            success=True,
            data={
                "investigation": serialize_value(
                    detail
                ),
                "routing": {
                    "should_investigate": (
                        decision.should_investigate
                    ),
                    "selected_specialists": list(
                        decision.selected_slugs
                    ),
                    "candidate_specialists": list(
                        decision.candidate_slugs
                    ),
                    "detected_domains": list(
                        decision.detected_domains
                    ),
                },
            },
        )

    async def _get_investigation(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        يجلب تفاصيل تحقيق محدد ويعيدها لعميل MCP.
        """
        detail = self._read_investigation(
            arguments
        )

        if detail is None:
            return ProjectToolResult(
                tool_id="get_investigation",
                success=False,
                error_code="investigation_not_found",
                error_message="Investigation not found.",
            )

        return ProjectToolResult(
            tool_id="get_investigation",
            success=True,
            data={
                "investigation": serialize_value(
                    detail
                )
            },
        )

    async def _get_investigation_status(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        يعيد الحالة المرحلية والنتيجة الحالية للتحقيق.
        """
        detail = self._read_investigation(
            arguments
        )

        if detail is None:
            return ProjectToolResult(
                tool_id="get_investigation_status",
                success=False,
                error_code="investigation_not_found",
                error_message="Investigation not found.",
            )

        return ProjectToolResult(
            tool_id="get_investigation_status",
            success=True,
            data={
                "investigation_id": (
                    detail.investigation_id
                ),
                "status": detail.status,
                "should_investigate": (
                    detail.should_investigate
                ),
                "runtime_available": (
                    detail.runtime_available
                ),
                "final_diagnosis_available": (
                    detail.final_diagnosis_available
                ),
                "selected_specialists": [
                    candidate.specialist_slug
                    for candidate in detail.candidates
                    if candidate.is_selected
                ],
                **self._specialist_progress(detail),
            },
        )
