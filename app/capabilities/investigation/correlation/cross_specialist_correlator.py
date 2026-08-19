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

from .claim_builder import CrossSpecialistClaimBuilder

class CrossSpecialistCorrelator:
    """
    يجمع نتائج الاختصاصيين في ادعاءات وتشخيص نهائي مع التحقق من الأدلة.
    """

    def __init__(self) -> None:
        self._claim_builder = CrossSpecialistClaimBuilder()

    def correlate(
        self,
        result: InvestigationExecutionResult,
    ) -> FinalDiagnosis:
        """
        يربط نتائج الاختصاصيين ويحسب الادعاءات والتعارضات والتشخيص النهائي.
        """
        evidence_by_id = {
            item.evidence_id: item
            for item in result.state.evidence
        }

        grouped: dict[
            str,
            list[
                tuple[
                    str,
                    InvestigationFinding,
                ]
            ],
        ] = {}

        completed_specialists: list[str] = []

        for run in result.runs:
            if (
                run.result.status
                != SpecialistTaskStatus.COMPLETED
            ):
                continue

            completed_specialists.append(
                run.specialist_slug
            )

            for finding in run.result.findings:
                self._claim_builder.validate_finding_evidence(
                    finding=finding,
                    evidence_by_id=evidence_by_id,
                )

                key = self._claim_builder.correlation_key(
                    finding
                )

                grouped.setdefault(
                    key,
                    [],
                ).append(
                    (
                        run.specialist_slug,
                        finding,
                    )
                )

        claims: list[
            CorrelatedDiagnosisClaim
        ] = []
        conflicts: list[
            DiagnosisConflict
        ] = []

        for index, (
            correlation_key,
            items,
        ) in enumerate(
            grouped.items(),
            start=1,
        ):
            claim, conflict = (
                self._claim_builder.build_claim(
                    investigation_id=(
                        result.state
                        .investigation_id
                    ),
                    index=index,
                    correlation_key=(
                        correlation_key
                    ),
                    items=items,
                )
            )

            claims.append(claim)

            if conflict is not None:
                conflicts.append(conflict)

        confirmed = sum(
            claim.certainty
            == DiagnosisCertainty.CONFIRMED
            for claim in claims
        )
        probable = sum(
            claim.certainty
            == DiagnosisCertainty.PROBABLE
            for claim in claims
        )
        unknown = sum(
            claim.certainty
            == DiagnosisCertainty.UNKNOWN
            for claim in claims
        )

        evidence_ids = tuple(
            dict.fromkeys(
                evidence_id
                for claim in claims
                for evidence_id
                in claim.evidence_ids
            )
        )
        code_locations = self._claim_builder.code_locations_from_claims(claims)
        remediation_actions = []
        for run in result.runs:
            raw_actions = (run.result.metadata or {}).get(
                "recommended_remediation_actions", []
            )
            if not isinstance(raw_actions, (list, tuple)):
                continue
            for action in raw_actions:
                if isinstance(action, dict):
                    remediation_actions.append(dict(action))

        return FinalDiagnosis(
            investigation_id=(
                result.state.investigation_id
            ),
            summary=self._build_summary(
                claims=claims,
                conflicts=conflicts,
                completed_specialists=tuple(
                    completed_specialists
                ),
            ),
            claims=tuple(claims),
            conflicts=tuple(conflicts),
            confirmed_count=confirmed,
            probable_count=probable,
            unknown_count=unknown,
            conflict_count=len(conflicts),
            evidence_ids=evidence_ids,
            specialist_slugs=tuple(
                dict.fromkeys(
                    completed_specialists
                )
            ),
            metadata={
                "correlator": (
                    "deterministic"
                ),
                "phase": "4.18.2",
                "specialist_result_count": (
                    len(
                        completed_specialists
                    )
                ),
                "claim_count": len(claims),
                "conflict_count": len(
                    conflicts
                ),
                "code_locations": code_locations,
                "recommended_remediation_actions": remediation_actions,
            },
        )


    def _validate_finding_evidence(self, **kwargs) -> None:
        """يحافظ على واجهة التحقق القديمة."""
        return self._claim_builder.validate_finding_evidence(**kwargs)

    def _build_claim(self, **kwargs):
        """يحافظ على واجهة بناء الادعاء القديمة."""
        return self._claim_builder.build_claim(**kwargs)

    @staticmethod
    def _code_locations_from_claims(claims) -> list[dict]:
        """يحافظ على واجهة جمع مواقع المصادر القديمة."""
        return CrossSpecialistClaimBuilder.code_locations_from_claims(claims)

    def _correlation_key(self, finding: InvestigationFinding) -> str:
        """يحافظ على واجهة إنشاء مفتاح الربط القديمة."""
        return self._claim_builder.correlation_key(finding)

    def _build_summary(
        self,
        *,
        claims: list[
            CorrelatedDiagnosisClaim
        ],
        conflicts: list[
            DiagnosisConflict
        ],
        completed_specialists: tuple[
            str,
            ...
        ],
    ) -> str:
        """
        ينشئ ملخصًا موجزًا للتشخيص من الادعاءات المقبولة.
        """
        if not completed_specialists:
            return (
                "No completed Specialist "
                "result is available for "
                "server-level correlation."
            )

        if not claims:
            return (
                "Specialist investigations "
                "completed, but no structured "
                "findings are available for "
                "a server-level diagnosis."
            )

        if conflicts:
            return (
                f"{len(conflicts)} explicit "
                "cross-Specialist conflict(s) "
                "remain unresolved; conflicting "
                "claims are classified as unknown."
            )

        confirmed = [
            claim
            for claim in claims
            if claim.certainty
            == DiagnosisCertainty.CONFIRMED
        ]

        probable = [
            claim
            for claim in claims
            if claim.certainty
            == DiagnosisCertainty.PROBABLE
        ]

        if confirmed:
            return (
                f"{len(confirmed)} confirmed "
                "claim(s) are supported by "
                "live Evidence; "
                f"{len(probable)} additional "
                "claim(s) remain probable."
            )

        if probable:
            return (
                "No claim reached the "
                "confirmed threshold; "
                f"{len(probable)} claim(s) "
                "are probable and supported "
                "by live Evidence."
            )

        return (
            "No live Evidence-backed "
            "diagnosis can be confirmed "
            "from the completed Specialist "
            "findings."
        )
