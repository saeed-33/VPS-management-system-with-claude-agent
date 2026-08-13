from tools.acceptance.evaluation.aggregate_readiness import (
    AggregateReadinessEvaluator,
)
from tools.acceptance.evaluation.contracts import (
    EvaluationMetric,
    EvaluationObservation,
    ReadinessStatus,
)


def obs(
    case_id,
    metric,
    *,
    passed=True,
):
    return EvaluationObservation(
        case_id=case_id,
        metric=metric,
        passed=passed,
        score=1.0 if passed else 0.0,
    )


def test_aggregate_combines_sources():
    persisted = (
        obs(
            "p1",
            EvaluationMetric
            .SPECIALIST_COMPLETION,
        ),
    )

    safety = (
        obs(
            "s1",
            EvaluationMetric
            .ROUTING_RECALL,
        ),
    )

    result = (
        AggregateReadinessEvaluator()
        .evaluate(
            persisted_observations=(
                persisted
            ),
            safety_observations=safety,
        )
    )

    assert len(
        result.observations
    ) == 2


def test_sample_deficits_are_reported():
    result = (
        AggregateReadinessEvaluator()
        .evaluate(
            persisted_observations=(
                obs(
                    "p1",
                    EvaluationMetric
                    .EVIDENCE_GROUNDING,
                ),
            ),
            safety_observations=(),
        )
    )

    assert (
        result.sample_deficits[
            EvaluationMetric
            .EVIDENCE_GROUNDING
        ]
        == 9
    )


def test_one_real_runtime_sample_is_not_ready():
    persisted = tuple(
        obs(
            f"p-{metric.value}",
            metric,
        )
        for metric in (
            EvaluationMetric
            .SPECIALIST_COMPLETION,
            EvaluationMetric
            .EVIDENCE_GROUNDING,
            EvaluationMetric
            .BUDGET_COMPLIANCE,
            EvaluationMetric
            .CONFLICT_PRESERVATION,
            EvaluationMetric
            .FINAL_DIAGNOSIS_GROUNDING,
        )
    )

    safety = tuple(
        obs(
            f"s-{metric.value}-{index}",
            metric,
        )
        for metric in (
            EvaluationMetric.ROUTING_RECALL,
            EvaluationMetric
            .PROVIDER_RESILIENCE,
            EvaluationMetric.POLICY_SAFETY,
        )
        for index in range(10)
    )

    result = (
        AggregateReadinessEvaluator()
        .evaluate(
            persisted_observations=(
                persisted
            ),
            safety_observations=safety,
        )
    )

    assert (
        result.readiness.status
        == ReadinessStatus
        .INSUFFICIENT_EVIDENCE
    )

    assert (
        result.readiness
        .automatic_remediation_allowed
        is False
    )


def test_hard_failure_blocks_when_samples_sufficient():
    persisted = []

    for metric, count in (
        (
            EvaluationMetric
            .SPECIALIST_COMPLETION,
            10,
        ),
        (
            EvaluationMetric
            .EVIDENCE_GROUNDING,
            10,
        ),
        (
            EvaluationMetric
            .BUDGET_COMPLIANCE,
            10,
        ),
        (
            EvaluationMetric
            .CONFLICT_PRESERVATION,
            5,
        ),
        (
            EvaluationMetric
            .FINAL_DIAGNOSIS_GROUNDING,
            10,
        ),
    ):
        for index in range(count):
            persisted.append(
                obs(
                    f"{metric.value}-{index}",
                    metric,
                    passed=not (
                        metric
                        == EvaluationMetric
                        .EVIDENCE_GROUNDING
                        and index == 0
                    ),
                )
            )

    safety = tuple(
        obs(
            f"{metric.value}-{index}",
            metric,
        )
        for metric in (
            EvaluationMetric.ROUTING_RECALL,
            EvaluationMetric
            .PROVIDER_RESILIENCE,
            EvaluationMetric.POLICY_SAFETY,
        )
        for index in range(10)
    )

    result = (
        AggregateReadinessEvaluator()
        .evaluate(
            persisted_observations=tuple(
                persisted
            ),
            safety_observations=safety,
        )
    )

    assert (
        result.readiness.status
        == ReadinessStatus.BLOCKED
    )
