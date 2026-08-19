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

class SpecialistReasoningResultBuilder:
    """يبني عقد النتيجة من مخرجات reasoning وسياق التحقيق."""

    @staticmethod
    def build(
        *,
        output: SpecialistReasoningOutput,
        context: SpecialistContextSnapshot,
        dropped_specialist_recommendations: tuple[str, ...] = (),
    ) -> SpecialistResult:
        """
        يحوّل استجابة النموذج إلى عقد تنفيذ اختصاصي.
        """
        evidence_by_id = {
            item.evidence_id: item
            for item in context.evidence
        }

        def finding_metadata(evidence_ids: tuple[str, ...]) -> dict:
            """
            يجمع البيانات الوصفية لمواقع الأدلة التي استند إليها الاكتشاف.
            """
            locations = []
            for evidence_id in evidence_ids:
                evidence = evidence_by_id.get(evidence_id)
                if evidence is None:
                    continue
                raw_locations = evidence.metadata.get("code_locations", [])
                if raw_locations:
                    for raw_location in raw_locations:
                        location = dict(raw_location)
                        location["evidence_ids"] = [evidence_id]
                        locations.append(location)
                elif evidence.excerpt:
                    locations.extend(
                        item.to_dict()
                        for item in extract_source_locations(
                            evidence.excerpt,
                            evidence_ids=(evidence_id,),
                        )
                    )
            unique = []
            seen = set()
            for location in locations:
                key = (
                    location.get("file_path"),
                    location.get("line_number"),
                    location.get("column_number"),
                    tuple(location.get("evidence_ids", [])),
                )
                if key not in seen:
                    seen.add(key)
                    unique.append(dict(location))
            return {"code_locations": unique} if unique else {}

        findings = tuple(
            InvestigationFinding(
                finding_id=(
                    f"{context.task_id}:finding:{index}"
                ),
                title=item.title,
                description=item.description,
                confidence=item.confidence,
                evidence_ids=tuple(item.evidence_ids),
                knowledge_source_ids=tuple(
                    item.knowledge_source_ids
                ),
                metadata=finding_metadata(tuple(item.evidence_ids)),
            )
            for index, item in enumerate(
                output.findings,
                start=1,
            )
        )

        hypotheses = tuple(
            InvestigationHypothesis(
                hypothesis_id=(
                    f"{context.task_id}:hypothesis:{index}"
                ),
                statement=item.statement,
                confidence=item.confidence,
                supporting_evidence_ids=tuple(
                    item.supporting_evidence_ids
                ),
                contradicting_evidence_ids=tuple(
                    item.contradicting_evidence_ids
                ),
            )
            for index, item in enumerate(
                output.hypotheses,
                start=1,
            )
        )

        used_evidence = tuple(
            dict.fromkeys(
                evidence_id
                for finding in findings
                for evidence_id in finding.evidence_ids
            )
        )
        used_knowledge = tuple(
            dict.fromkeys(
                source_id
                for finding in findings
                for source_id in finding.knowledge_source_ids
            )
        )

        remediation_actions = [
            item.model_dump(mode="json")
            for item in output.recommended_remediation_actions
        ]
        derived_action = (
            SpecialistReasoningResultBuilder.explicit_inactive_service_action(
                context=context,
            )
        )
        if derived_action is not None:
            action_key = (
                derived_action["action_type"],
                derived_action["target"],
            )
            existing_keys = {
                (
                    item.get("action_type"),
                    item.get("target"),
                )
                for item in remediation_actions
                if isinstance(item, dict)
            }
            if action_key not in existing_keys:
                remediation_actions.append(derived_action)

        return SpecialistResult(
            task_id=context.task_id,
            specialist_id=context.specialist_slug,
            status=SpecialistTaskStatus.COMPLETED,
            summary=output.summary,
            confidence=output.confidence,
            findings=findings,
            hypotheses=hypotheses,
            ruled_out=tuple(output.ruled_out),
            evidence_ids=used_evidence,
            knowledge_source_ids=used_knowledge,
            missing_evidence=tuple(output.missing_evidence),
            recommended_next_specialists=tuple(
                output.recommended_next_specialists
            ),
            metadata={
                "reasoning_only": True,
                "context_characters": context.character_count,
                "diagnostic_tool_request_count": len(
                    output.diagnostic_tool_requests
                ),
                "dropped_specialist_recommendations": list(
                    dropped_specialist_recommendations
                ),
                "recommended_remediation_actions": remediation_actions,
            },
        )

    @staticmethod
    def explicit_inactive_service_action(
        *,
        context: SpecialistContextSnapshot,
    ) -> dict | None:
        """
        ينشئ اقتراح بدء آمن عند وجود حالة متوقعة صريحة ودليل خدمة مسماة.

        لا يكفي أن تكون الخدمة inactive؛ يجب أن يثبت هدف التحقيق أو التحليل
        أن الحالة المطلوبة هي active، حتى لا نحول خدمة متوقفة عمداً إلى خطة
        تشغيل غير مقصودة.
        """
        if context.specialist_slug != "systemd-service":
            return None

        expectation_text_parts = [
            str(getattr(context, "objective", "") or ""),
            str(getattr(context, "initial_analysis_summary", "") or ""),
        ]
        for issue in getattr(context, "initial_analysis_issues", ()):
            if isinstance(issue, dict):
                expectation_text_parts.extend(
                    str(issue.get(key) or "")
                    for key in ("title", "description", "reason")
                )

        expectation_text = " ".join(expectation_text_parts).casefold()
        expected_active_markers = (
            r"\b(?:expected|should|must|required)\b.{0,60}\b(?:active|running)\b",
            r"\b(?:active|running)\b.{0,60}\b(?:expected|required|must)\b",
            r"\b(?:restore|start|bring)\b.{0,60}\b(?:service|unit)\b",
            r"\b(?:service|unit)\b.{0,60}\b(?:start|running|active|required)\b",
            r"(?:يجب|ينبغي|مطلوب|من المفترض).{0,60}(?:تعمل|نشطة|قيد التشغيل|التشغيل)",
            r"(?:تشغيل|بدء).{0,40}(?:الخدمة|الوحدة)",
            r"(?:الخدمة|الوحدة).{0,40}(?:تعمل|نشطة|قيد التشغيل)",
        )
        if not any(
            re.search(marker, expectation_text, flags=re.IGNORECASE | re.DOTALL)
            for marker in expected_active_markers
        ):
            return None

        inactive_markers = (
            "inactive (dead)",
            "active: inactive",
            "inactive",
        )
        command_pattern = re.compile(
            r"\bsystemctl\s+(?:--\S+\s+)*status\s+"
            r"([A-Za-z0-9][A-Za-z0-9_.@-]{0,127})\b",
            flags=re.IGNORECASE,
        )

        for evidence in context.evidence:
            metadata = dict(evidence.metadata or {})
            if str(metadata.get("tool_id") or "").casefold() != "systemd-status":
                continue
            excerpt = str(evidence.excerpt or "").casefold()
            if not any(marker in excerpt for marker in inactive_markers):
                continue
            command_text = str(metadata.get("command_text") or "")
            match = command_pattern.search(command_text)
            if match is None:
                continue
            target = match.group(1)
            if not SERVICE_NAME_RE.fullmatch(target):
                continue
            return {
                "action_type": "start_service",
                "target": target,
                "reason": (
                    "The investigation explicitly requires this service to "
                    "be active, while systemd-status evidence shows it is "
                    "inactive."
                ),
                "expected_effect": "The named systemd service becomes active.",
                "risk_level": "low",
                "requires_approval": True,
                "rollback_supported": True,
                "verification_strategy": (
                    "Verify the service state is active after approval."
                ),
                "evidence_requirements": [evidence.evidence_id],
            }

        return None
