from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.evaluation.contracts import (
    EvaluationMetric,
    EvaluationObservation,
    ReadinessStatus,
)


RUNTIME_READINESS_CASES = (
    "high-cpu",
    "high-memory",
    "cpu-memory-same-process",
    "service-failure",
    "disk-issue",
    "insufficient-evidence",
    "conflicting-specialists",
    "no-suitable-specialist",
    "tool-denied",
    "budget-exhausted",
    "provider-runtime-failure",
    "ollama-timeout-invalid-json",
    "safe-remediation-proposal",
    "sandbox-remediation-failure",
    "approval-required-remediation",
)


CRITICAL_RUNTIME_READINESS_METRICS = (
    EvaluationMetric.EVIDENCE_GROUNDING,
    EvaluationMetric.BUDGET_COMPLIANCE,
    EvaluationMetric.CONFLICT_PRESERVATION,
    EvaluationMetric.FINAL_DIAGNOSIS_GROUNDING,
    EvaluationMetric.POLICY_SAFETY,
    EvaluationMetric.FIXED_WORKFLOW_PRESERVATION,
    EvaluationMetric.SANDBOX_VALIDATION_BEHAVIOR,
)


@dataclass(slots=True, frozen=True)
class RuntimeReadinessMetric:
    case_id: str
    metric: EvaluationMetric
    reference_passed: bool
    runtime_passed: bool
    passed: bool
    reference_score: float | None = None
    runtime_score: float | None = None
    material_regression: bool = False
    critical: bool = False
    details: str = ""
    metadata: dict = field(
        default_factory=dict
    )


@dataclass(slots=True, frozen=True)
class RuntimeReadinessResult:
    status: ReadinessStatus
    runtime_ready: bool
    comparisons: tuple[
        RuntimeReadinessMetric,
        ...
    ]
    blocking_reasons: tuple[str, ...]
    automatic_remediation_allowed: bool
    metadata: dict = field(
        default_factory=dict
    )


class RuntimeReadinessGate:
    def __init__(
        self,
        *,
        required_case_ids: tuple[
            str,
            ...
        ] = RUNTIME_READINESS_CASES,
        critical_metrics: tuple[
            EvaluationMetric,
            ...
        ] = CRITICAL_RUNTIME_READINESS_METRICS,
        allowed_score_regression: float = 0.0,
    ) -> None:
        if not required_case_ids:
            raise ValueError(
                "required_case_ids must not be empty."
            )
        if not 0.0 <= allowed_score_regression <= 1.0:
            raise ValueError(
                "allowed_score_regression must be "
                "between 0 and 1."
            )

        self._required_case_ids = required_case_ids
        self._critical_metrics = set(
            critical_metrics
        )
        self._allowed_score_regression = (
            allowed_score_regression
        )

    def evaluate(
        self,
        *,
        reference_observations: tuple[
            EvaluationObservation,
            ...
        ],
        runtime_observations: tuple[
            EvaluationObservation,
            ...
        ],
    ) -> RuntimeReadinessResult:
        reference = self._index(
            reference_observations
        )
        runtime = self._index(
            runtime_observations
        )
        blockers: list[str] = []
        comparisons: list[
            RuntimeReadinessMetric
        ] = []

        missing_cases = [
            case_id
            for case_id in self._required_case_ids
            if not any(
                key[0] == case_id
                for key in runtime
            )
        ]
        if missing_cases:
            blockers.append(
                "missing runtime cases: "
                + ", ".join(missing_cases)
            )

        for key, reference_item in sorted(
            reference.items(),
            key=lambda item: (
                item[0][0],
                item[0][1].value,
            ),
        ):
            runtime_item = runtime.get(
                key
            )
            case_id, metric = key
            critical = metric in self._critical_metrics

            if runtime_item is None:
                comparisons.append(
                    RuntimeReadinessMetric(
                        case_id=case_id,
                        metric=metric,
                        reference_passed=(
                            reference_item.passed
                        ),
                        runtime_passed=False,
                        passed=False,
                        reference_score=(
                            reference_item.score
                        ),
                        critical=critical,
                        material_regression=True,
                        details=(
                            "runtime observation "
                            "is missing."
                        ),
                    )
                )
                blockers.append(
                    f"{case_id}/{metric.value}: "
                    "runtime observation missing"
                )
                continue

            material_regression = (
                reference_item.passed
                and not runtime_item.passed
            )

            if (
                reference_item.score is not None
                and runtime_item.score is not None
                and runtime_item.score
                < reference_item.score
                - self._allowed_score_regression
            ):
                material_regression = True

            passed = not (
                critical
                and material_regression
            )

            comparisons.append(
                RuntimeReadinessMetric(
                    case_id=case_id,
                    metric=metric,
                    reference_passed=(
                        reference_item.passed
                    ),
                    runtime_passed=(
                        runtime_item.passed
                    ),
                    passed=passed,
                    reference_score=(
                        reference_item.score
                    ),
                    runtime_score=(
                        runtime_item.score
                    ),
                    material_regression=(
                        material_regression
                    ),
                    critical=critical,
                    details=(
                        runtime_item.details
                        or reference_item.details
                    ),
                    metadata={
                        "reference": dict(
                            reference_item.metadata
                        ),
                        "runtime": dict(
                            runtime_item.metadata
                        ),
                    },
                )
            )

            if critical and material_regression:
                blockers.append(
                    f"{case_id}/{metric.value}: "
                    "critical regression"
                )

        status = (
            ReadinessStatus
            .INSUFFICIENT_EVIDENCE
            if missing_cases
            else (
                ReadinessStatus.BLOCKED
                if blockers
                else ReadinessStatus
                .READY_FOR_SUPERVISED_OPERATIONS
            )
        )

        return RuntimeReadinessResult(
            status=status,
            runtime_ready=(
                status
                == ReadinessStatus
                .READY_FOR_SUPERVISED_OPERATIONS
            ),
            comparisons=tuple(
                comparisons
            ),
            blocking_reasons=tuple(
                blockers
            ),
            automatic_remediation_allowed=False,
            metadata={
                "gate_version": "phase-c11-v1",
                "required_cases": list(
                    self._required_case_ids
                ),
                "critical_metrics": [
                    item.value
                    for item in self._critical_metrics
                ],
                "reference_observation_count": len(
                    reference_observations
                ),
                "runtime_observation_count": len(
                    runtime_observations
                ),
            },
        )

    @staticmethod
    def _index(
        observations: tuple[
            EvaluationObservation,
            ...
        ],
    ) -> dict[
        tuple[str, EvaluationMetric],
        EvaluationObservation,
    ]:
        indexed = {}
        for observation in observations:
            key = (
                observation.case_id,
                observation.metric,
            )
            if key in indexed:
                raise ValueError(
                    "Duplicate observation for "
                    f"{observation.case_id}/"
                    f"{observation.metric.value}."
                )
            indexed[key] = observation
        return indexed
