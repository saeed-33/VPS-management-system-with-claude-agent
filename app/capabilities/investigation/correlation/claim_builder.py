"""Class extracted from correlation during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import re

from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.investigation_finding import InvestigationFinding
from app.core.contracts.investigation.specialist_task_status import SpecialistTaskStatus

from app.capabilities.investigation.execution_contracts.investigation_execution_result import InvestigationExecutionResult

from .correlated_diagnosis_claim import CorrelatedDiagnosisClaim

from .diagnosis_certainty import DiagnosisCertainty

from .diagnosis_conflict import DiagnosisConflict

from .final_diagnosis import FinalDiagnosis

class CrossSpecialistClaimBuilder:
    """يبني الادعاءات والتعارضات من نتائج الاختصاصيين."""

    def validate_finding_evidence(
        self,
        *,
        finding: InvestigationFinding,
        evidence_by_id: dict[
            str,
            EvidenceReference,
        ],
    ) -> None:
        """
        يتحقق من أن كل ملاحظة تشخيصية تشير إلى دليل قابل للتتبع.
        """
        unknown = [
            evidence_id
            for evidence_id
            in finding.evidence_ids
            if evidence_id
            not in evidence_by_id
        ]

        if unknown:
            raise ValueError(
                "Correlation received finding "
                "with unknown evidence IDs: "
                + ", ".join(unknown)
            )

    def build_claim(
        self,
        *,
        investigation_id: str,
        index: int,
        correlation_key: str,
        items: list[
            tuple[
                str,
                InvestigationFinding,
            ]
        ],
    ) -> tuple[
        CorrelatedDiagnosisClaim,
        DiagnosisConflict | None,
    ]:
        """
        يبني ادعاء تشخيص من نتيجة اختصاصي ومراجعها.
        """
        specialist_slugs = tuple(
            dict.fromkeys(
                slug
                for slug, _ in items
            )
        )

        evidence_ids = tuple(
            dict.fromkeys(
                evidence_id
                for _, finding in items
                for evidence_id
                in finding.evidence_ids
            )
        )

        knowledge_ids = tuple(
            dict.fromkeys(
                source_id
                for _, finding in items
                for source_id
                in finding.knowledge_source_ids
            )
        )

        missing = tuple(
            dict.fromkeys(
                item
                for _, finding in items
                for item
                in finding.missing_evidence
            )
        )

        confidence = max(
            finding.confidence
            for _, finding in items
        )

        representative = max(
            (
                finding
                for _, finding in items
            ),
            key=lambda item: (
                item.confidence
            ),
        )

        states = tuple(
            dict.fromkeys(
                str(
                    finding.metadata.get(
                        "diagnostic_state",
                        "",
                    )
                ).strip()
                for _, finding in items
                if str(
                    finding.metadata.get(
                        "diagnostic_state",
                        "",
                    )
                ).strip()
            )
        )

        conflict = None

        if len(states) > 1:
            certainty = (
                DiagnosisCertainty.UNKNOWN
            )

            conflict = DiagnosisConflict(
                conflict_id=(
                    f"{investigation_id}:"
                    f"conflict:{index}"
                ),
                title=representative.title,
                diagnostic_states=states,
                specialist_slugs=(
                    specialist_slugs
                ),
                evidence_ids=evidence_ids,
                source_finding_ids=tuple(
                    finding.finding_id
                    for _, finding
                    in items
                ),
                description=(
                    "Specialists reported "
                    "different explicit "
                    "diagnostic states for "
                    f"{correlation_key!r}."
                ),
            )

        elif evidence_ids:
            certainty = (
                DiagnosisCertainty.CONFIRMED
                if confidence >= 0.80
                else DiagnosisCertainty.PROBABLE
            )

        else:
            certainty = (
                DiagnosisCertainty.UNKNOWN
            )

        code_locations = self.code_locations(items)

        return (
            CorrelatedDiagnosisClaim(
                claim_id=(
                    f"{investigation_id}:"
                    f"claim:{index}"
                ),
                title=(
                    representative.title
                ),
                description=(
                    representative.description
                ),
                certainty=certainty,
                confidence=confidence,
                specialist_slugs=(
                    specialist_slugs
                ),
                evidence_ids=evidence_ids,
                knowledge_source_ids=(
                    knowledge_ids
                ),
                missing_evidence=missing,
                metadata={
                    "source_finding_ids": [
                        finding.finding_id
                        for _, finding
                        in items
                    ],
                    "correlated_specialist_count": (
                        len(
                            specialist_slugs
                        )
                    ),
                    "diagnostic_states": list(
                        states
                    ),
                    "conflict": (
                        conflict is not None
                    ),
                    "code_locations": code_locations,
                },
            ),
            conflict,
        )

    @staticmethod
    def code_locations_from_claims(claims) -> list[dict]:
        """
        يجمع مواقع المصادر من الادعاءات المرتبطة.
        """
        locations = []
        seen = set()
        for claim in claims:
            for location in (claim.metadata or {}).get("code_locations", []):
                key = (
                    location.get("file_path"),
                    location.get("line_number"),
                    location.get("column_number"),
                    tuple(location.get("evidence_ids", [])),
                )
                if key not in seen:
                    seen.add(key)
                    locations.append(dict(location))
        return locations

    @staticmethod
    def code_locations(items) -> list[dict]:
        """
        يستخرج مواقع الملفات والأسطر من نصوص الأدلة.
        """
        locations = []
        seen = set()
        for _, finding in items:
            for location in (finding.metadata or {}).get("code_locations", []):
                location_evidence_ids = tuple(location.get("evidence_ids", []))
                if any(
                    evidence_id not in finding.evidence_ids
                    for evidence_id in location_evidence_ids
                ):
                    continue
                key = (
                    location.get("file_path"),
                    location.get("line_number"),
                    location.get("column_number"),
                    tuple(location.get("evidence_ids", [])),
                )
                if key not in seen:
                    seen.add(key)
                    locations.append(dict(location))
        return locations

    def correlation_key(
        self,
        finding: InvestigationFinding,
    ) -> str:
        """
        ينشئ مفتاح تجميع ثابتًا لادعاء أو ملاحظة تشخيصية.
        """
        text = finding.title.lower()

        tokens = re.findall(
            r"[a-z0-9]"
            r"[a-z0-9._:-]*",
            text,
        )

        stop = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "of",
            "to",
            "for",
            "and",
            "or",
            "on",
            "in",
            "with",
            "status",
            "check",
            "unknown",
        }

        meaningful = [
            token
            for token in tokens
            if token not in stop
        ]

        return (
            " ".join(
                meaningful[:8]
            )
            or finding.finding_id
        )
