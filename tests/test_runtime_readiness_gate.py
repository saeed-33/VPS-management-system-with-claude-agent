from app.domain.evaluation import (
    EvaluationMetric,
    EvaluationObservation,
    RUNTIME_READINESS_CASES,
    RuntimeReadinessGate,
    ReadinessStatus,
)


CRITICAL_SAMPLE_METRICS = (
    EvaluationMetric.EVIDENCE_GROUNDING,
    EvaluationMetric.POLICY_SAFETY,
    EvaluationMetric.FIXED_WORKFLOW_PRESERVATION,
    EvaluationMetric.SANDBOX_VALIDATION_BEHAVIOR,
)


def observations(
    *,
    fail_case=None,
    fail_metric=None,
    omit_case=None,
    score_drop_case=None,
    score_drop_metric=None,
):
    items = []
    for case_id in RUNTIME_READINESS_CASES:
        if case_id == omit_case:
            continue
        for metric in CRITICAL_SAMPLE_METRICS:
            passed = not (
                case_id == fail_case
                and metric == fail_metric
            )
            score = 1.0
            if (
                case_id == score_drop_case
                and metric == score_drop_metric
            ):
                score = 0.5
            items.append(
                EvaluationObservation(
                    case_id=case_id,
                    metric=metric,
                    passed=passed,
                    score=score,
                )
            )
    return tuple(items)


def test_runtime_readiness_gate_passes_full_non_regressing_matrix():
    result = RuntimeReadinessGate().evaluate(
        reference_observations=observations(),
        runtime_observations=observations(),
    )

    assert (
        result.status
        == ReadinessStatus
        .READY_FOR_SUPERVISED_OPERATIONS
    )
    assert result.runtime_ready is True
    assert (
        result.automatic_remediation_allowed
        is False
    )
    assert result.blocking_reasons == ()


def test_runtime_readiness_gate_blocks_missing_runtime_case():
    result = RuntimeReadinessGate().evaluate(
        reference_observations=observations(),
        runtime_observations=observations(
            omit_case="disk-issue"
        ),
    )

    assert (
        result.status
        == ReadinessStatus.INSUFFICIENT_EVIDENCE
    )
    assert result.runtime_ready is False
    assert any(
        "disk-issue" in item
        for item in result.blocking_reasons
    )


def test_runtime_readiness_gate_blocks_critical_regression():
    result = RuntimeReadinessGate().evaluate(
        reference_observations=observations(),
        runtime_observations=observations(
            fail_case="tool-denied",
            fail_metric=(
                EvaluationMetric.POLICY_SAFETY
            ),
        ),
    )

    assert result.status == ReadinessStatus.BLOCKED
    assert result.runtime_ready is False
    assert any(
        "tool-denied/policy_safety"
        in item
        for item in result.blocking_reasons
    )


def test_runtime_readiness_gate_blocks_critical_score_regression():
    result = RuntimeReadinessGate().evaluate(
        reference_observations=observations(),
        runtime_observations=observations(
            score_drop_case=(
                "sandbox-remediation-failure"
            ),
            score_drop_metric=(
                EvaluationMetric
                .SANDBOX_VALIDATION_BEHAVIOR
            ),
        ),
    )

    assert result.status == ReadinessStatus.BLOCKED
    assert any(
        comparison.material_regression
        for comparison in result.comparisons
        if comparison.case_id
        == "sandbox-remediation-failure"
    )


def test_non_critical_regression_is_recorded_but_does_not_block():
    reference = observations() + (
        EvaluationObservation(
            case_id="high-cpu",
            metric=EvaluationMetric.LATENCY,
            passed=True,
            score=1.0,
        ),
    )
    runtime = observations() + (
        EvaluationObservation(
            case_id="high-cpu",
            metric=EvaluationMetric.LATENCY,
            passed=False,
            score=0.1,
        ),
    )

    result = RuntimeReadinessGate().evaluate(
        reference_observations=reference,
        runtime_observations=runtime,
    )

    assert (
        result.status
        == ReadinessStatus
        .READY_FOR_SUPERVISED_OPERATIONS
    )
    assert any(
        comparison.material_regression
        and not comparison.critical
        for comparison in result.comparisons
    )


def test_duplicate_observations_are_rejected():
    duplicate = observations() + (
        EvaluationObservation(
            case_id="high-cpu",
            metric=(
                EvaluationMetric
                .EVIDENCE_GROUNDING
            ),
            passed=True,
        ),
    )

    try:
        RuntimeReadinessGate().evaluate(
            reference_observations=duplicate,
            runtime_observations=observations(),
        )
    except ValueError as exc:
        assert (
            "Duplicate observation"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Duplicate observations accepted."
        )
