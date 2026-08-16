"""
جزء من Investigation/Specialist لتوجيه التحقيق وجمع Evidence وبناء التشخيص.

الموقع في المعمارية: Application capability / investigation.
يُستدعى بواسطة: MCP أو Analysis workflow.
يعتمد مباشرة على: app.core.contracts.investigation، app.capabilities.investigation.execution_contracts.
الحد المعماري: لا يتجاوز Diagnostic Policy؛ Python يتحقق وينفذ collection.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
    يمثل DiagnosisCertainty مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على StrEnum وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    CONFIRMED = "confirmed"
    PROBABLE = "probable"
    UNKNOWN = "unknown"


@dataclass(slots=True, frozen=True)
class DiagnosisConflict:
    """
    يمثل DiagnosisConflict مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يمثل CorrelatedDiagnosisClaim مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يمثل FinalDiagnosis مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    Deterministic, provenance-first cross-Specialist correlator.

    Certainty:
    - confirmed: live Evidence and confidence >= 0.80;
    - probable: live Evidence and confidence < 0.80;
    - unknown: no live Evidence, or an explicit conflict.

    Conflict detection is explicit rather than inferred from prose.
    Specialists may attach:

        metadata={"diagnostic_state": "present"}

    or another domain-specific state. Different non-empty states for
    the same correlation key create a DiagnosisConflict.
    """

    def correlate(
        self,
        result: InvestigationExecutionResult,
    ) -> FinalDiagnosis:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى correlate؛ المدخلات المهمة: result.
        تعيد FinalDiagnosis أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _validate_finding_evidence؛ المدخلات المهمة: finding، evidence_by_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _build_claim؛ المدخلات المهمة: investigation_id، index، correlation_key، items.
        تعيد tuple[CorrelatedDiagnosisClaim, DiagnosisConflict | None] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _code_locations_from_claims؛ المدخلات المهمة: claims.
        تعيد list[dict] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _code_locations؛ المدخلات المهمة: items.
        تعيد list[dict] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _correlation_key؛ المدخلات المهمة: finding.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _build_summary؛ المدخلات المهمة: claims، conflicts، completed_specialists.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
