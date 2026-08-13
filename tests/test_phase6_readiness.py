from tools.acceptance.evaluation.phase6_readiness import Phase6Metric, Phase6Observation, Phase6ReadinessGate


def test_phase6_real_runtime_blocker_keeps_gate_closed():
    observations = [Phase6Observation(metric, 1, 1) for metric in Phase6Metric]
    result = Phase6ReadinessGate().evaluate(observations, real_acceptance_status="BLOCKED_BY_SANDBOX_RUNTIME")
    assert result["status"] == "BLOCKED"
    assert result["automatic_remediation_allowed"] is False


def test_phase6_gate_requires_all_thirteen_metrics():
    result = Phase6ReadinessGate().evaluate([], real_acceptance_status="PASS")
    assert len(result["blocking_reasons"]) == 13
