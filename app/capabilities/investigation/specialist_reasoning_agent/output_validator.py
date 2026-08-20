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

from app.core.contracts.specialist_reasoning.specialist_reasoning_client import (
    SpecialistReasoningClient,
)

from app.core.contracts.specialist_reasoning.specialist_reasoning_output import SpecialistReasoningOutput

from app.core.policies.remediation_tools.constants import SERVICE_NAME_RE

from app.capabilities.investigation.source_location import extract_source_locations

from .specialist_diagnostic_tool_request import SpecialistDiagnosticToolRequest

from .specialist_reasoning_execution import SpecialistReasoningExecution

from .reasoning_prompt import SYSTEM_PROMPT

class SpecialistReasoningOutputValidator:
    """يتحقق من مراجع مخرجات الاختصاصي ويوحد توصيات المجالات."""

    @staticmethod
    def validate_references(
        *,
        output: SpecialistReasoningOutput,
        context: SpecialistContextSnapshot,
        allowed_specialist_slugs: tuple[str, ...],
    ) -> None:
        """
        يتحقق من أن مراجع النتيجة تشير إلى أدلة أو مواقع موجودة.
        """
        evidence_ids = {
            item.evidence_id
            for item in context.evidence
        }
        knowledge_ids = {
            item.source_id
            for item in context.knowledge_sources
        }

        def normalize_reference(
            value: str,
            *,
            namespace: str,
            allowed: set[str],
        ) -> str:
            """
            يطبع مرجعًا ويزيل بادئته مع التأكد من بقائه ضمن الأدلة المسموحة.
            """
            candidate = value.strip()

            prefix = namespace + ":"

            if candidate.startswith(prefix):
                suffix = candidate[len(prefix):]

                # لا نقبل تطبيع المعرف إلا إذا ظل يشير إلى دليل حقيقي موجود
                # في سياق التحقيق المقدم.
                if suffix in allowed:
                    return suffix

            return candidate

        for finding in output.findings:
            finding.evidence_ids = [
                normalize_reference(
                    value,
                    namespace="evidence",
                    allowed=evidence_ids,
                )
                for value in finding.evidence_ids
            ]

            finding.knowledge_source_ids = [
                normalize_reference(
                    value,
                    namespace="knowledge",
                    allowed=knowledge_ids,
                )
                for value in finding.knowledge_source_ids
            ]
            unknown_evidence = (
                set(finding.evidence_ids)
                - evidence_ids
            )
            unknown_knowledge = (
                set(finding.knowledge_source_ids)
                - knowledge_ids
            )

            if unknown_evidence:
                raise ValueError(
                    "Specialist reasoning referenced unknown evidence IDs: "
                    + ", ".join(sorted(unknown_evidence))
                )

            if unknown_knowledge:
                raise ValueError(
                    "Specialist reasoning referenced unknown knowledge IDs: "
                    + ", ".join(sorted(unknown_knowledge))
                )

        for hypothesis in output.hypotheses:
            hypothesis.supporting_evidence_ids = [
                normalize_reference(
                    value,
                    namespace="evidence",
                    allowed=evidence_ids,
                )
                for value in hypothesis.supporting_evidence_ids
            ]

            hypothesis.contradicting_evidence_ids = [
                normalize_reference(
                    value,
                    namespace="evidence",
                    allowed=evidence_ids,
                )
                for value in hypothesis.contradicting_evidence_ids
            ]

            unknown = (
                set(hypothesis.supporting_evidence_ids)
                | set(hypothesis.contradicting_evidence_ids)
            ) - evidence_ids

            if unknown:
                raise ValueError(
                    "Specialist hypothesis referenced unknown evidence IDs: "
                    + ", ".join(sorted(unknown))
                )

    @staticmethod
    def normalize_specialist_recommendations(
        *,
        recommendations: tuple[str, ...],
        allowed_specialist_slugs: tuple[str, ...],
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """
        يطبع توصيات الاختصاصي إلى شكل آمن موحد.
        """
        allowed = {
            value.strip().casefold()
            for value in allowed_specialist_slugs
            if value.strip()
        }

        aliases = {
            "systemd": "systemd-service",
            "service": "systemd-service",
            "services": "systemd-service",
            "network": "linux-network",
            "networking": "linux-network",
            "cpu": "linux-cpu",
            "processor": "linux-cpu",
            "memory": "linux-memory",
            "ram": "linux-memory",
            "storage": "linux-storage",
            "disk": "linux-storage",
            "filesystem": "linux-storage",
            "process": "linux-process",
            "processes": "linux-process",
            "postgres": "postgresql",
            "postgresql": "postgresql",
            "nginx": "nginx",
            "docker": "docker",
        }

        accepted: list[str] = []
        dropped: list[str] = []

        for raw in recommendations:
            value = raw.strip().casefold()
            if not value:
                continue

            candidate = aliases.get(value, value)

            if candidate in allowed:
                if candidate not in accepted:
                    accepted.append(candidate)
            else:
                dropped.append(value)

        return (
            tuple(accepted),
            tuple(dict.fromkeys(dropped)),
        )
