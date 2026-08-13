from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from tools.acceptance.evaluation.cases import (
    EvaluationCase,
)
from tools.acceptance.evaluation.contracts import (
    EvaluationMetric,
    EvaluationObservation,
    ProductionReadinessResult,
)
from tools.acceptance.evaluation.readiness_gate import (
    ProductionReadinessGate,
)


@dataclass(slots=True, frozen=True)
class EvaluationCaseResult:
    case_id: str
    passed: bool
    details: str = ""
    score: float | None = None


CaseExecutor = Callable[
    [EvaluationCase],
    EvaluationCaseResult,
]


@dataclass(slots=True, frozen=True)
class EvaluationRunResult:
    cases_total: int
    cases_passed: int
    observations: tuple[
        EvaluationObservation,
        ...
    ]
    readiness: ProductionReadinessResult


class DeterministicEvaluationRunner:
    """
    Dataset runner for Phase 4.20.

    It does not execute production runtime by itself.
    A CaseExecutor decides each fixture result.
    Phase 4.20.3 supplies a runtime-backed executor.
    """

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

    def run(
        self,
        *,
        cases: tuple[
            EvaluationCase,
            ...
        ],
        executor: CaseExecutor,
    ) -> EvaluationRunResult:
        if not cases:
            raise ValueError(
                "At least one EvaluationCase "
                "is required."
            )

        case_ids = [
            item.case_id
            for item in cases
        ]

        if len(case_ids) != len(
            set(case_ids)
        ):
            raise ValueError(
                "Duplicate EvaluationCase IDs "
                "are not allowed."
            )

        observations = []
        passed_cases = 0

        for case in cases:
            result = executor(case)

            if (
                result.case_id
                != case.case_id
            ):
                raise ValueError(
                    "Executor returned a result "
                    "for the wrong case_id."
                )

            if result.passed:
                passed_cases += 1

            for metric in (
                case.expected_metrics
            ):
                observations.append(
                    EvaluationObservation(
                        case_id=case.case_id,
                        metric=metric,
                        passed=result.passed,
                        score=result.score,
                        details=result.details,
                        metadata={
                            "case_title": (
                                case.title
                            ),
                            "case_category": (
                                case.category
                            ),
                            **case.metadata,
                        },
                    )
                )

        readiness = self._gate.evaluate(
            tuple(observations)
        )

        return EvaluationRunResult(
            cases_total=len(cases),
            cases_passed=passed_cases,
            observations=tuple(
                observations
            ),
            readiness=readiness,
        )


def expected_behavior_executor(
    case: EvaluationCase,
) -> EvaluationCaseResult:
    """
    Deterministic dataset-validation executor.

    This proves dataset completeness and gate wiring only.
    It is not a runtime quality measurement.
    """
    return EvaluationCaseResult(
        case_id=case.case_id,
        passed=case.expected_pass,
        score=(
            1.0
            if case.expected_pass
            else 0.0
        ),
        details=(
            "Dataset expectation accepted."
        ),
    )
