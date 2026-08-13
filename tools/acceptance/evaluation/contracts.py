from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EvaluationMetric(StrEnum):
    ROUTING_RECALL = "routing_recall"
    SPECIALIST_COMPLETION = "specialist_completion"
    EVIDENCE_GROUNDING = "evidence_grounding"
    BUDGET_COMPLIANCE = "budget_compliance"
    CONFLICT_PRESERVATION = "conflict_preservation"
    FINAL_DIAGNOSIS_GROUNDING = "final_diagnosis_grounding"
    PROVIDER_RESILIENCE = "provider_resilience"
    POLICY_SAFETY = "policy_safety"
    FIXED_WORKFLOW_PRESERVATION = (
        "fixed_workflow_preservation"
    )
    SANDBOX_VALIDATION_BEHAVIOR = (
        "sandbox_validation_behavior"
    )
    LATENCY = "latency"
    TOOL_CALLS = "tool_calls"
    COST = "cost"


class ReadinessStatus(StrEnum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    BLOCKED = "blocked"
    READY_FOR_SUPERVISED_OPERATIONS = (
        "ready_for_supervised_operations"
    )


@dataclass(slots=True, frozen=True)
class EvaluationObservation:
    case_id: str
    metric: EvaluationMetric
    passed: bool
    score: float | None = None
    details: str = ""
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError(
                "case_id must not be empty."
            )

        if (
            self.score is not None
            and not 0.0 <= self.score <= 1.0
        ):
            raise ValueError(
                "score must be between 0 and 1."
            )


@dataclass(slots=True, frozen=True)
class MetricThreshold:
    metric: EvaluationMetric
    minimum_pass_rate: float
    minimum_samples: int
    hard_block_on_any_failure: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.minimum_pass_rate <= 1.0:
            raise ValueError(
                "minimum_pass_rate must be between 0 and 1."
            )

        if self.minimum_samples < 1:
            raise ValueError(
                "minimum_samples must be >= 1."
            )


@dataclass(slots=True, frozen=True)
class MetricEvaluation:
    metric: EvaluationMetric
    samples: int
    passed_samples: int
    pass_rate: float
    required_pass_rate: float
    required_samples: int
    hard_block_on_any_failure: bool
    sufficient_samples: bool
    threshold_met: bool
    hard_block_triggered: bool


@dataclass(slots=True, frozen=True)
class ProductionReadinessResult:
    status: ReadinessStatus
    metrics: tuple[MetricEvaluation, ...]
    blocking_reasons: tuple[str, ...]
    automatic_remediation_allowed: bool
    metadata: dict[str, Any] = field(
        default_factory=dict
    )
