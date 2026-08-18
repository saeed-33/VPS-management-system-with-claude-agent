"""
ربط نتائج الاختصاصيين في تشخيص نهائي قابل للتدقيق.

يقارن الملف الادعاءات والأدلة والتعارضات بين الاختصاصيين، ويمنع بناء نتيجة
نهائية من ملاحظة لا تحمل مرجع دليل صالحًا.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from app.core.contracts.investigation import (
    EvidenceReference,
    InvestigationFinding,
    SpecialistTaskStatus,
)
from app.capabilities.investigation.execution_contracts import (
    InvestigationExecutionResult,
)


class DiagnosisCertainty(StrEnum):
    """
    يمثل درجات اليقين الممكنة في ادعاء التشخيص النهائي.
    """
    CONFIRMED = "confirmed"
    PROBABLE = "probable"
    UNKNOWN = "unknown"


@dataclass(slots=True, frozen=True)
class DiagnosisConflict:
    """
    يمثل تعارضًا بين نتائج اختصاصيين حول الحقل أو السبب أو الدليل.
    """
    conflict_id: str
    title: str
    diagnostic_states: tuple[str, ...]
    specialist_slugs: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    source_finding_ids: tuple[str, ...]
    description: str

    def __post_init__(self) -> None:
        """
        يتحقق من صحة بيانات DiagnosisConflict قبل استخدامها في التحقيق.
        """
        if not self.conflict_id.strip():
            raise ValueError(
                "conflict_id must not be empty."
            )
        if not self.title.strip():
            raise ValueError(
                "Conflict title must not be empty."
            )
        if len(self.diagnostic_states) < 2:
            raise ValueError(
                "A conflict requires at least two states."
            )


@dataclass(slots=True, frozen=True)
class CorrelatedDiagnosisClaim:
    """
    يمثل ادعاء تشخيصي بعد ربطه بمصادر وأدلة الاختصاصيين.
    """
    claim_id: str
    title: str
    description: str
    certainty: DiagnosisCertainty
    confidence: float
    specialist_slugs: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    knowledge_source_ids: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    metadata: dict | None = None

    def __post_init__(self) -> None:
        """
        يتحقق من صحة بيانات CorrelatedDiagnosisClaim قبل استخدامها في التحقيق.
        """
        if not self.claim_id.strip():
            raise ValueError(
                "claim_id must not be empty."
            )
        if not self.title.strip():
            raise ValueError(
                "Claim title must not be empty."
            )
        if not self.description.strip():
            raise ValueError(
                "Claim description must not be empty."
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Claim confidence must be between 0 and 1."
            )
        if self.metadata is None:
            object.__setattr__(
                self,
                "metadata",
                {},
            )


@dataclass(slots=True, frozen=True)
class FinalDiagnosis:
    """
    يمثل التشخيص النهائي المجمع مع الادعاءات والتعارضات ومواقع المصادر.
    """
    investigation_id: str
    summary: str
    claims: tuple[
        CorrelatedDiagnosisClaim,
        ...
    ]
    conflicts: tuple[
        DiagnosisConflict,
        ...
    ]
    confirmed_count: int
    probable_count: int
    unknown_count: int
    conflict_count: int
    evidence_ids: tuple[str, ...]
    specialist_slugs: tuple[str, ...]
    metadata: dict

    def __post_init__(self) -> None:
        """
        يتحقق من صحة بيانات FinalDiagnosis قبل استخدامها في التحقيق.
        """
        if not self.investigation_id.strip():
            raise ValueError(
                "investigation_id must not be empty."
            )
        if not self.summary.strip():
            raise ValueError(
                "Final diagnosis summary must not be empty."
            )
        if self.conflict_count != len(
            self.conflicts
        ):
            raise ValueError(
                "conflict_count must match conflicts."
            )


class CrossSpecialistCorrelator:
    """
    يجمع نتائج الاختصاصيين في ادعاءات وتشخيص نهائي مع التحقق من الأدلة.
    """

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
                self._validate_finding_evidence(
                    finding=finding,
                    evidence_by_id=evidence_by_id,
                )

                key = self._correlation_key(
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
                self._build_claim(
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
        code_locations = self._code_locations_from_claims(claims)
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

    def _validate_finding_evidence(
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

    def _build_claim(
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

        code_locations = self._code_locations(items)

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
    def _code_locations_from_claims(claims) -> list[dict]:
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
    def _code_locations(items) -> list[dict]:
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

    def _correlation_key(
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
