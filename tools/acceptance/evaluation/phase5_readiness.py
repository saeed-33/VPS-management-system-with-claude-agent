from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, Iterable


class Phase5Metric(StrEnum):
    PROPOSAL_VALIDITY = "proposal_validity"
    RISK_CLASSIFICATION = "risk_classification"
    APPROVAL_INTEGRITY = "approval_integrity"
    POLICY_ENFORCEMENT = "policy_enforcement"
    WRITE_TOOL_SAFETY = "write_tool_safety"
    EXECUTION_INTEGRITY = "execution_integrity"
    IDEMPOTENCY = "idempotency"
    EVIDENCE_COMPLETENESS = "evidence_completeness"
    VERIFICATION_CORRECTNESS = "verification_correctness"
    ROLLBACK_CORRECTNESS = "rollback_correctness"
    AUDIT_COMPLETENESS = "audit_completeness"
    MCP_SAFETY = "mcp_safety"
    REAL_SUPERVISED_REMEDIATION = "real_supervised_remediation"


CRITICAL_PHASE5_METRICS = frozenset(Phase5Metric)


@dataclass(frozen=True, slots=True)
class Phase5Observation:
    metric: Phase5Metric
    numerator: int
    denominator: int
    threshold: float = 1.0
    details: str = ""
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.denominator < 1 or self.numerator < 0 or self.numerator > self.denominator:
            raise ValueError("Phase 5 observation counts are invalid.")
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("Phase 5 threshold must be between 0 and 1.")

    @property
    def score(self) -> float:
        return self.numerator / self.denominator


@dataclass(frozen=True, slots=True)
class Phase5MetricResult:
    metric: Phase5Metric
    numerator: int
    denominator: int
    score: float
    threshold: float
    passed: bool
    critical: bool
    details: str
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class Phase5ReadinessResult:
    status: str
    metrics: tuple[Phase5MetricResult, ...]
    blocking_reasons: tuple[str, ...]
    automatic_remediation_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "automatic_remediation_allowed": self.automatic_remediation_allowed,
            "blocking_reasons": list(self.blocking_reasons),
            "metrics": [asdict(metric) for metric in self.metrics],
        }


class Phase5ReadinessGate:
    def evaluate(self, observations: Iterable[Phase5Observation], *, real_acceptance_status: str) -> Phase5ReadinessResult:
        indexed = {item.metric: item for item in observations}
        results: list[Phase5MetricResult] = []
        blockers: list[str] = []
        for metric in Phase5Metric:
            observation = indexed.get(metric)
            if observation is None:
                blockers.append(f"{metric.value}: observation missing")
                continue
            passed = observation.score >= observation.threshold
            if metric == Phase5Metric.REAL_SUPERVISED_REMEDIATION and real_acceptance_status != "PASS":
                passed = False
            result = Phase5MetricResult(
                metric=metric,
                numerator=observation.numerator,
                denominator=observation.denominator,
                score=observation.score,
                threshold=observation.threshold,
                passed=passed,
                critical=metric in CRITICAL_PHASE5_METRICS,
                details=observation.details,
                metadata=dict(observation.metadata or {}),
            )
            results.append(result)
            if not passed:
                blockers.append(f"{metric.value}: threshold not met")
        if real_acceptance_status == "BLOCKED_BY_SAFE_TEST_ENVIRONMENT":
            blockers.append("real supervised remediation: safe test environment unavailable")
        return Phase5ReadinessResult(
            status="READY_FOR_SUPERVISED_OPERATIONS" if not blockers else "BLOCKED",
            metrics=tuple(results),
            blocking_reasons=tuple(dict.fromkeys(blockers)),
            automatic_remediation_allowed=False,
        )
