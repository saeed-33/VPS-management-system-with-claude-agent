from __future__ import annotations

from dataclasses import dataclass

from app.domain.evaluation.contracts import (
    EvaluationMetric,
    EvaluationObservation,
    ProductionReadinessResult,
)
from app.domain.evaluation.readiness_gate import (
    ProductionReadinessGate,
)


@dataclass(slots=True, frozen=True)
class AggregateEvaluationResult:
    persisted_observations: tuple[
        EvaluationObservation,
        ...
    ]
    safety_observations: tuple[
        EvaluationObservation,
        ...
    ]
    observations: tuple[
        EvaluationObservation,
        ...
    ]
    readiness: ProductionReadinessResult
    sample_deficits: dict[
        EvaluationMetric,
        int,
    ]


class AggregateReadinessEvaluator:
    def __init__(
        self,
        *,
        gate: ProductionReadinessGate
        | None = None,
    ) -> None:
        self._gate = (
            gate
            or ProductionReadinessGate()
        )

    def evaluate(
        self,
        *,
        persisted_observations: tuple[
            EvaluationObservation,
            ...
        ],
        safety_observations: tuple[
            EvaluationObservation,
            ...
        ],
    ) -> AggregateEvaluationResult:
        observations = (
            *persisted_observations,
            *safety_observations,
        )

        readiness = self._gate.evaluate(
            observations
        )

        deficits = {}

        for metric in readiness.metrics:
            deficits[metric.metric] = max(
                0,
                metric.required_samples
                - metric.samples,
            )

        return AggregateEvaluationResult(
            persisted_observations=(
                persisted_observations
            ),
            safety_observations=(
                safety_observations
            ),
            observations=tuple(
                observations
            ),
            readiness=readiness,
            sample_deficits=deficits,
        )
