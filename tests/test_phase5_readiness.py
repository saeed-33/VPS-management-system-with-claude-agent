from tools.acceptance.evaluation.phase5_readiness import (
    Phase5Metric,
    Phase5Observation,
    Phase5ReadinessGate,
)


def test_phase5_gate_requires_all_metrics_and_real_acceptance():
    observations = [Phase5Observation(metric, 1, 1) for metric in Phase5Metric]
    blocked = Phase5ReadinessGate().evaluate(
        observations,
        real_acceptance_status="BLOCKED_BY_SAFE_TEST_ENVIRONMENT",
    )
    assert blocked.status == "BLOCKED"
    assert any("safe test environment" in reason for reason in blocked.blocking_reasons)
    assert blocked.automatic_remediation_allowed is False


def test_phase5_gate_passes_only_with_explicit_real_acceptance():
    observations = [Phase5Observation(metric, 1, 1) for metric in Phase5Metric]
    ready = Phase5ReadinessGate().evaluate(observations, real_acceptance_status="PASS")
    assert ready.status == "READY_FOR_SUPERVISED_OPERATIONS"
    assert all(metric.passed for metric in ready.metrics)
