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


class _InvestigationToolsOperations3:
    """ينظم مجموعة من عمليات التحقيق في MCP."""

    async def _run_specialist(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        يشغل اختصاصيًا ضمن تحقيق وفق وسائط الأداة.
        """
        self._require_dependency(
            self._specialist_investigation_loop,
            "specialist_investigation_loop",
        )
        self._require_dependency(
            self._analysis_repository,
            "analysis_repository",
        )

        detail = self._read_investigation(
            arguments
        )
        if detail is None:
            return ProjectToolResult(
                tool_id="run_specialist",
                success=False,
                error_code="investigation_not_found",
                error_message="Investigation not found.",
            )

        specialist = self._specialist_by_slug(
            arguments
        )
        if specialist is None:
            return ProjectToolResult(
                tool_id="run_specialist",
                success=False,
                error_code="specialist_not_found",
                error_message=(
                    "Enabled Specialist definition "
                    "was not found."
                ),
            )

        selected_slugs = {
            candidate.specialist_slug
            for candidate in detail.candidates
            if candidate.is_selected
        }
        if specialist.slug not in selected_slugs:
            return ProjectToolResult(
                tool_id="run_specialist",
                success=False,
                error_code="specialist_not_selected",
                error_message=(
                    "Specialist was not selected by "
                    "the investigation routing decision."
                ),
            )

        objective = arguments.get("objective")
        if not isinstance(objective, str) or not objective.strip():
            raise ValueError(
                "objective must be a non-empty string."
            )

        analysis = (
            self._analysis_repository.get_by_id(
                detail.analysis_id
            )
            if detail.analysis_id is not None
            else self._analysis_repository
            .get_by_report_id(detail.report_id)
        )
        if analysis is None:
            return ProjectToolResult(
                tool_id="run_specialist",
                success=False,
                error_code="analysis_not_found",
                error_message=(
                    "Analysis is required before "
                    "running a Specialist."
                ),
            )

        execution_service = getattr(
            self,
            "_specialist_execution_service",
            None,
        )
        ownership_token = None
        if execution_service is not None:
            reservation = execution_service.reserve_with_token(
                investigation_id=detail.investigation_id,
                specialist_slug=specialist.slug,
            )
            if reservation["status"] == "completed":
                return ProjectToolResult(
                    tool_id="run_specialist",
                    success=True,
                    data={
                        "specialist": serialize_specialist_definition(specialist),
                        "result": reservation.get("run"),
                        "persisted": True,
                        "idempotent": True,
                        "runtime": self._specialist_progress(detail),
                    },
                )
            if reservation["status"] == "in_progress":
                return ProjectToolResult(
                    tool_id="run_specialist",
                    success=False,
                    error_code="specialist_in_progress",
                    error_message=(
                        "This Specialist is already reserved by another "
                        "worker; read persisted investigation status and retry "
                        "only if the lease expires."
                    ),
                )
            ownership_token = reservation["ownership_token"]
            investigation_actions_used = int(reservation.get("actions_used") or 0)

        if execution_service is None and detail.runtime is not None:
            investigation_actions_used = (
                detail.runtime.actions_used or 0
            )
        elif execution_service is None:
            investigation_actions_used = 0

        task = SpecialistTask(
            task_id=(
                f"{detail.investigation_id}:"
                f"{specialist.slug}:1"
            ),
            investigation_id=detail.investigation_id,
            server_id=detail.server_id,
            report_id=detail.report_id,
            specialist_id=specialist.slug,
            objective=objective.strip(),
            trigger_issue_ids=tuple(
                str(index)
                for candidate in detail.candidates
                if (
                    candidate.specialist_slug
                    == specialist.slug
                )
                for index in (
                    candidate.matched_issue_indexes
                )
            ),
            knowledge_topics=(
                specialist.knowledge_topics
            ),
            status=SpecialistTaskStatus.RUNNING,
            metadata={
                "source": "claude_code_mcp",
                "specialist_definition_id": (
                    specialist.id
                ),
            },
        )

        try:
            result = await (
                self._specialist_investigation_loop.run(
                    task=task,
                    specialist=specialist,
                    investigation_budget=InvestigationBudget(
                        max_specialists=detail.max_specialists,
                        max_rounds=detail.max_rounds,
                        max_actions=detail.max_actions,
                    ),
                    detected_domains=detail.detected_domains,
                    initial_analysis_summary=analysis.summary,
                    initial_analysis_issues=tuple(analysis.issues or []),
                    allowed_specialist_slugs=tuple(selected_slugs),
                    investigation_actions_used=investigation_actions_used,
                )
            )
        except Exception as exc:
            if execution_service is None or ownership_token is None:
                raise
            persisted = await execution_service.finalize_failure(
                task=task,
                reason=str(exc),
                selected_specialists=tuple(selected_slugs),
                ownership_token=ownership_token,
            )
            return ProjectToolResult(
                tool_id="run_specialist",
                success=False,
                data={"result": persisted["run"], "runtime": persisted["snapshot"]},
                error_code="specialist_execution_failed",
                error_message=str(exc),
            )

        persisted = None
        if execution_service is not None and ownership_token is not None:
            persisted = await execution_service.finalize(
                task=task,
                loop_result=result,
                selected_specialists=tuple(selected_slugs),
                ownership_token=ownership_token,
            )

        return ProjectToolResult(
            tool_id="run_specialist",
            success=True,
            data={
                "task": serialize_value(task),
                "specialist": (
                    serialize_specialist_definition(
                        specialist
                    )
                ),
                "result": (
                    serialize_specialist_loop_result(
                        result
                    )
                ),
                "persisted_result": (
                    persisted["run"]
                    if persisted is not None
                    else None
                ),
                "runtime": (
                    persisted["snapshot"]
                    if persisted is not None
                    else None
                ),
            },
        )
