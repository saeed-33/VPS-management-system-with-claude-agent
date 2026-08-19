"""Class extracted from specialist_reasoning_agent during the structure refactor."""

from __future__ import annotations

import re

from dataclasses import dataclass

from app.core.contracts.investigation.investigation_finding import InvestigationFinding
from app.core.contracts.investigation.investigation_hypothesis import InvestigationHypothesis
from app.core.contracts.investigation.specialist_result import SpecialistResult
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus

from app.core.policies.diagnostic_tools.diagnostic_tool_call import DiagnosticToolCall

from app.capabilities.investigation.specialist_context.specialist_context_snapshot import SpecialistContextSnapshot

from app.capabilities.investigation.specialist_reasoning_client import (
    SpecialistReasoningClient,
)

from app.core.contracts.specialist_reasoning.specialist_reasoning_output import SpecialistReasoningOutput

from app.core.policies.remediation_tools.constants import SERVICE_NAME_RE

from app.capabilities.investigation.source_location import extract_source_locations

from .specialist_diagnostic_tool_request import SpecialistDiagnosticToolRequest

from .specialist_reasoning_execution import SpecialistReasoningExecution

from .constants import SYSTEM_PROMPT

from .output_validator import SpecialistReasoningOutputValidator
from .result_builder import SpecialistReasoningResultBuilder

class SpecialistReasoningAgent:
    """
    يتحقق من استجابة الاختصاصي ويحوّلها إلى نتيجة تشخيصية قابلة للحفظ.
    """

    _REFERENCE_RETRY_LIMIT = 1

    def __init__(
        self,
        *,
        client: SpecialistReasoningClient,
    ) -> None:
        """
        يهيئ SpecialistReasoningAgent ويربط الاعتماديات اللازمة لدورة التحقيق.
        """
        self._client = client
        self._validator = SpecialistReasoningOutputValidator()
        self._result_builder = SpecialistReasoningResultBuilder()

    async def reason(
        self,
        *,
        context: SpecialistContextSnapshot,
        allowed_specialist_slugs: tuple[str, ...] = (),
        diagnostic_tool_catalog: str | None = None,
        force_final_synthesis: bool = False,
    ) -> SpecialistReasoningExecution:
        """
        ينفذ reasoning الاختصاصي ويتحقق من المراجع ويعيد النتيجة المنظمة.
        """
        user_prompt = (
            "## Mandatory Investigation Objective\n"
            + context.objective
            + (
                "\n\nThis Objective is the task to solve. "
                "Do not replace it with a generic incident, "
                "a connectivity problem, or a description of "
                "the available Tools. Your summary and every "
                "diagnostic action must directly advance this "
                "Objective.\n\n"
            )
            + context.rendered_context
        )

        evidence_ids = tuple(
            dict.fromkeys(
                item.evidence_id
                for item in context.evidence
            )
        )
        knowledge_source_ids = tuple(
            dict.fromkeys(
                item.source_id
                for item in context.knowledge_sources
            )
        )
        user_prompt += (
            "\n\n## Evidence ID Allowlist\n"
            "The only valid values for finding.evidence_ids, "
            "hypothesis.supporting_evidence_ids, and "
            "hypothesis.contradicting_evidence_ids are the exact opaque "
            "Evidence IDs listed below. Copy the identifier token only. "
            "Never copy an Evidence title, observation, excerpt, command, "
            "status line, hostname, or any other raw text into an Evidence "
            "ID field. If no listed ID supports a statement, return an empty "
            "list.\n"
            "Allowed Evidence IDs: "
            + (
                ", ".join(
                    f"`{value}`"
                    for value in evidence_ids
                )
                if evidence_ids
                else "(none)"
            )
            + "\n\n## Knowledge Source ID Allowlist\n"
            "The only valid values for finding.knowledge_source_ids are "
            "the exact opaque Knowledge Source IDs listed below. Copy the "
            "identifier token only. Never copy a source label, title, "
            "excerpt, Initial Issues text, or prose into a Knowledge Source "
            "ID field. If no listed source supports a statement, return an "
            "empty list.\n"
            "Allowed Knowledge Source IDs: "
            + (
                ", ".join(
                    f"`{value}`"
                    for value in knowledge_source_ids
                )
                if knowledge_source_ids
                else "(none)"
            )
        )

        if force_final_synthesis:
            user_prompt += (
                "\n\n## Final Synthesis Required\n"
                "No further diagnostic execution is available in this pass. "
                "Do not request any Diagnostic Tool. Produce a short final "
                "diagnostic conclusion using only the current Evidence.\n"
                "\n## Final Synthesis Size Limits\n"
                "- summary: at most 350 characters.\n"
                "- findings: at most 2.\n"
                "- each finding description: at most 240 characters.\n"
                "- hypotheses: at most 1.\n"
                "- ruled_out: at most 2.\n"
                "- missing_evidence: at most 3 short items.\n"
                "- recommended_next_specialists: at most 1 enabled slug, "
                "and only when another Specialist domain is genuinely "
                "required.\n"
                "- diagnostic_tool_requests: always empty.\n"
                "\n## Provenance Rules For Final Synthesis\n"
                "Evidence IDs and Knowledge Source IDs are opaque identifiers. "
                "Copy them exactly from explicit `evidence_id:` or "
                "`knowledge_source_id:` fields in the context. Never derive "
                "an ID from a module name, command name, hostname, prose, or "
                "documentation content. If no exact Knowledge Source ID is "
                "needed, use an empty knowledge_source_ids list. Do not copy "
                "or paraphrase long command output into the response."
            )

        if diagnostic_tool_catalog and not force_final_synthesis:
            user_prompt += (
                "\n\n## Available Diagnostic Tools\n"
                + diagnostic_tool_catalog
                + (
                    "\n\n## Objective Reminder\n"
                    + context.objective
                    + (
                        "\nSelect only the minimum directly relevant "
                        "Tool evidence needed to answer this Objective. "
                        "The Tool catalog is capability metadata, not the "
                        "problem statement."
                    )
                )
            )

        output = await self._client.reason(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        for attempt in range(
            self._REFERENCE_RETRY_LIMIT + 1
        ):
            try:
                self._validator.validate_references(
                    output=output,
                    context=context,
                    allowed_specialist_slugs=(
                        allowed_specialist_slugs
                    ),
                )
                break
            except ValueError:
                if attempt >= self._REFERENCE_RETRY_LIMIT:
                    raise

                # لا نحاول تخمين المعرف من مخرجات الأمر. نعيد الطلب إلى
                # النموذج مع تذكير صريح بالقائمة المسموحة، ثم نبقي التحقق
                # الصارم فعالًا على المحاولة الثانية أيضًا.
                output = await self._client.reason(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=(
                        user_prompt
                        + "\n\n## Provenance Correction Required\n"
                        "The previous JSON used raw text or an unknown value "
                        "as an Evidence ID or Knowledge Source ID. Return "
                        "the same diagnostic result as one JSON object, but "
                        "use only exact opaque IDs from the Evidence ID "
                        "Allowlist and Knowledge Source ID Allowlist. "
                        "If an observation has no matching ID, use an empty "
                        "list and add the observation to missing_evidence. "
                        "If no exact Knowledge Source ID is available, use "
                        "an empty knowledge_source_ids list. Never put "
                        "command output, process text, labels, or a "
                        "description in an ID field."
                    ),
                )

        normalized_specialists, dropped_specialists = (
            self._validator.normalize_specialist_recommendations(
                recommendations=tuple(
                    output.recommended_next_specialists
                ),
                allowed_specialist_slugs=(
                    allowed_specialist_slugs
                ),
            )
            if allowed_specialist_slugs
            else (
                tuple(output.recommended_next_specialists),
                (),
            )
        )

        output.recommended_next_specialists = list(
            normalized_specialists
        )

        result = self._result_builder.build(
            output=output,
            context=context,
            dropped_specialist_recommendations=(
                dropped_specialists
            ),
        )

        diagnostic_requests = tuple(
            SpecialistDiagnosticToolRequest(
                call=DiagnosticToolCall(
                    tool_id=item.tool_id,
                    arguments=dict(
                        item.arguments
                    ),
                ),
                rationale=item.rationale,
            )
            for item
            in output.diagnostic_tool_requests
        )

        if force_final_synthesis:
            diagnostic_requests = ()

        return SpecialistReasoningExecution(
            result=result,
            provider=self._client.provider_name,
            model=self._client.model_name,
            diagnostic_tool_requests=(
                diagnostic_requests
            ),
        )


    @staticmethod
    def _validate_references(**kwargs) -> None:
        """يحافظ على واجهة التحقق القديمة."""
        return SpecialistReasoningOutputValidator.validate_references(**kwargs)

    @staticmethod
    def _normalize_specialist_recommendations(**kwargs):
        """يحافظ على واجهة تطبيع التوصيات القديمة."""
        return SpecialistReasoningOutputValidator.normalize_specialist_recommendations(**kwargs)

    @staticmethod
    def _to_result(**kwargs) -> SpecialistResult:
        """يحافظ على واجهة بناء النتيجة القديمة."""
        return SpecialistReasoningResultBuilder.build(**kwargs)

    @staticmethod
    def _explicit_inactive_service_action(**kwargs) -> dict | None:
        """يحافظ على واجهة اشتقاق إجراء الخدمة القديمة."""
        return SpecialistReasoningResultBuilder.explicit_inactive_service_action(**kwargs)
