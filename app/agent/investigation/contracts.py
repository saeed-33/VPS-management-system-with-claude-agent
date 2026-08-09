from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class InvestigationStatus(StrEnum):
    CREATED = "created"
    INVESTIGATING = "investigating"
    WAITING_FOR_EVIDENCE = "waiting_for_evidence"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SpecialistTaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EvidenceKind(StrEnum):
    MONITORING_REPORT = "monitoring_report"
    COMMAND_RESULT = "command_result"
    ANALYSIS = "analysis"
    HISTORICAL_INCIDENT = "historical_incident"
    KNOWLEDGE_DOCUMENT = "knowledge_document"
    DERIVED_FINDING = "derived_finding"


class KnowledgeSourceType(StrEnum):
    INCIDENT = "incident"
    INTERNAL_DOCUMENT = "internal_document"
    OFFICIAL_DOCUMENTATION = "official_documentation"
    EXTERNAL_REFERENCE = "external_reference"


@dataclass(slots=True, frozen=True)
class InvestigationBudget:
    max_specialists: int = 4
    max_rounds: int = 3
    max_actions: int = 12

    def __post_init__(self) -> None:
        if self.max_specialists < 1:
            raise ValueError(
                "max_specialists must be >= 1."
            )
        if self.max_rounds < 1:
            raise ValueError(
                "max_rounds must be >= 1."
            )
        if self.max_actions < 0:
            raise ValueError(
                "max_actions must be >= 0."
            )


@dataclass(slots=True, frozen=True)
class EvidenceReference:
    evidence_id: str
    kind: EvidenceKind
    title: str
    source_id: int | str | None = None
    excerpt: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError(
                "evidence_id must not be empty."
            )
        if not self.title.strip():
            raise ValueError(
                "Evidence title must not be empty."
            )


@dataclass(slots=True, frozen=True)
class KnowledgeSourceReference:
    source_id: str
    source_type: KnowledgeSourceType
    title: str
    url: str | None = None
    topic: str | None = None
    product: str | None = None
    version: str | None = None
    trust_level: str | None = None
    excerpt: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError(
                "source_id must not be empty."
            )
        if not self.title.strip():
            raise ValueError(
                "Knowledge source title must not be empty."
            )


@dataclass(slots=True, frozen=True)
class InvestigationFinding:
    finding_id: str
    title: str
    description: str
    confidence: float
    evidence_ids: tuple[str, ...] = ()
    knowledge_source_ids: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.finding_id.strip():
            raise ValueError(
                "finding_id must not be empty."
            )
        if not self.title.strip():
            raise ValueError(
                "Finding title must not be empty."
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Finding confidence must be between 0 and 1."
            )


@dataclass(slots=True, frozen=True)
class InvestigationHypothesis:
    hypothesis_id: str
    statement: str
    confidence: float
    supporting_evidence_ids: tuple[str, ...] = ()
    contradicting_evidence_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip():
            raise ValueError(
                "hypothesis_id must not be empty."
            )
        if not self.statement.strip():
            raise ValueError(
                "Hypothesis statement must not be empty."
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Hypothesis confidence must be between 0 and 1."
            )


@dataclass(slots=True, frozen=True)
class SpecialistTask:
    task_id: str
    investigation_id: str
    server_id: int
    report_id: int
    specialist_id: str
    objective: str
    trigger_issue_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    knowledge_topics: tuple[str, ...] = ()
    round_number: int = 1
    status: SpecialistTaskStatus = (
        SpecialistTaskStatus.PENDING
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError(
                "task_id must not be empty."
            )
        if not self.investigation_id.strip():
            raise ValueError(
                "investigation_id must not be empty."
            )
        if self.server_id < 1:
            raise ValueError(
                "server_id must be >= 1."
            )
        if self.report_id < 1:
            raise ValueError(
                "report_id must be >= 1."
            )
        if not self.specialist_id.strip():
            raise ValueError(
                "specialist_id must not be empty."
            )
        if not self.objective.strip():
            raise ValueError(
                "Specialist objective must not be empty."
            )
        if self.round_number < 1:
            raise ValueError(
                "round_number must be >= 1."
            )


@dataclass(slots=True, frozen=True)
class SpecialistResult:
    task_id: str
    specialist_id: str
    status: SpecialistTaskStatus
    summary: str
    confidence: float
    findings: tuple[InvestigationFinding, ...] = ()
    hypotheses: tuple[
        InvestigationHypothesis,
        ...
    ] = ()
    ruled_out: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    knowledge_source_ids: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    recommended_next_specialists: tuple[
        str,
        ...
    ] = ()
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError(
                "task_id must not be empty."
            )
        if not self.specialist_id.strip():
            raise ValueError(
                "specialist_id must not be empty."
            )
        if not self.summary.strip():
            raise ValueError(
                "Specialist summary must not be empty."
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Specialist confidence must be between 0 and 1."
            )

        if self.status == SpecialistTaskStatus.PENDING:
            raise ValueError(
                "SpecialistResult cannot have pending status."
            )


@dataclass(slots=True)
class ServerInvestigationState:
    investigation_id: str
    server_id: int
    report_id: int
    analysis_id: int | None
    status: InvestigationStatus = (
        InvestigationStatus.CREATED
    )
    round_number: int = 1
    budget: InvestigationBudget = field(
        default_factory=InvestigationBudget
    )
    detected_domains: list[str] = field(
        default_factory=list
    )
    evidence: list[EvidenceReference] = field(
        default_factory=list
    )
    knowledge_sources: list[
        KnowledgeSourceReference
    ] = field(default_factory=list)
    tasks: list[SpecialistTask] = field(
        default_factory=list
    )
    results: list[SpecialistResult] = field(
        default_factory=list
    )
    final_findings: list[
        InvestigationFinding
    ] = field(default_factory=list)
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.investigation_id.strip():
            raise ValueError(
                "investigation_id must not be empty."
            )
        if self.server_id < 1:
            raise ValueError(
                "server_id must be >= 1."
            )
        if self.report_id < 1:
            raise ValueError(
                "report_id must be >= 1."
            )
        if self.analysis_id is not None:
            if self.analysis_id < 1:
                raise ValueError(
                    "analysis_id must be >= 1 when provided."
                )
        if self.round_number < 1:
            raise ValueError(
                "round_number must be >= 1."
            )

    def add_evidence(
        self,
        evidence: EvidenceReference,
    ) -> None:
        if any(
            item.evidence_id == evidence.evidence_id
            for item in self.evidence
        ):
            raise ValueError(
                "Duplicate evidence_id: "
                f"{evidence.evidence_id}"
            )

        self.evidence.append(evidence)

    def add_knowledge_source(
        self,
        source: KnowledgeSourceReference,
    ) -> None:
        if any(
            item.source_id == source.source_id
            for item in self.knowledge_sources
        ):
            raise ValueError(
                "Duplicate knowledge source_id: "
                f"{source.source_id}"
            )

        self.knowledge_sources.append(source)

    def add_task(
        self,
        task: SpecialistTask,
    ) -> None:
        if task.investigation_id != self.investigation_id:
            raise ValueError(
                "Task belongs to a different investigation."
            )

        if task.server_id != self.server_id:
            raise ValueError(
                "Task belongs to a different server."
            )

        if task.report_id != self.report_id:
            raise ValueError(
                "Task belongs to a different report."
            )

        if task.round_number > self.budget.max_rounds:
            raise ValueError(
                "Task exceeds investigation round budget."
            )

        if any(
            item.task_id == task.task_id
            for item in self.tasks
        ):
            raise ValueError(
                f"Duplicate task_id: {task.task_id}"
            )

        specialist_ids = {
            item.specialist_id
            for item in self.tasks
        }

        if (
            task.specialist_id not in specialist_ids
            and len(specialist_ids)
            >= self.budget.max_specialists
        ):
            raise ValueError(
                "Investigation specialist budget exceeded."
            )

        self.tasks.append(task)

    def add_result(
        self,
        result: SpecialistResult,
    ) -> None:
        matching_task = next(
            (
                task
                for task in self.tasks
                if task.task_id == result.task_id
            ),
            None,
        )

        if matching_task is None:
            raise ValueError(
                "Result does not reference a known task."
            )

        if (
            matching_task.specialist_id
            != result.specialist_id
        ):
            raise ValueError(
                "Result specialist does not match task specialist."
            )

        if any(
            item.task_id == result.task_id
            for item in self.results
        ):
            raise ValueError(
                "A result already exists for task_id: "
                f"{result.task_id}"
            )

        self.results.append(result)
