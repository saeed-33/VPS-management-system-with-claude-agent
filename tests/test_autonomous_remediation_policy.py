from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.core.contracts.autonomous_remediation import (
    AutonomousDecisionOutcome,
    AutonomousEvaluationContext,
    AutonomousHistorySnapshot,
    AutonomousPolicyStatus,
    AutonomousRemediationPolicy,
)
from app.core.policies.autonomous_remediation import AutonomousRemediationPolicyEvaluator


NOW = datetime(2026, 8, 14, tzinfo=timezone.utc)


def policy(**updates):
    values = {
        "policy_id": "policy-1",
        "name": "Start nginx",
        "description": "safe lab policy",
        "status": AutonomousPolicyStatus.ENABLED,
        "version": 1,
        "issue_fingerprint": "issue-1",
        "allowed_action_type": "start_service",
        "allowed_target_pattern": "nginx",
        "minimum_success_count": 1,
        "maximum_failure_rate": 0.0,
        "allowed_server_ids": (4,),
    }
    values.update(updates)
    return AutonomousRemediationPolicy(**values)


def context(**updates):
    values = {
        "global_enabled": True,
        "now": NOW,
        "policy": policy(),
        "plan_id": "plan-1",
        "plan_fingerprint": "fp-1",
        "issue_fingerprint": "issue-1",
        "server_id": 4,
        "action_type": "start_service",
        "target": "nginx",
        "risk": "low",
        "confidence": 0.95,
        "diagnosis_evidence_valid": True,
        "plan_evidence_valid": True,
        "sandbox": SimpleNamespace(
            status="passed", plan_id="plan-1", plan_fingerprint="fp-1",
            server_id=4, service="nginx", action_type="start_service",
            before_evidence_ids=["before"], after_evidence_ids=["after"],
            verification_status="verified", created_at=NOW,
        ),
        "sandbox_evidence_valid": True,
        "history": AutonomousHistorySnapshot(
            issue_fingerprint="issue-1", action_type="start_service", target="nginx",
            supervised_execution_count=1, successful_execution_count=1,
            verified_success_count=1,
        ),
        "plan_ready": True,
    }
    values.update(updates)
    return AutonomousEvaluationContext(**values)


def test_valid_low_risk_context_auto_executes():
    result = AutonomousRemediationPolicyEvaluator().evaluate(context())
    assert result.outcome is AutonomousDecisionOutcome.AUTO_EXECUTE
    assert "policy_match" in result.reason_codes


def test_global_kill_switch_denies_even_with_valid_policy():
    result = AutonomousRemediationPolicyEvaluator().evaluate(context(global_enabled=False))
    assert result.outcome is AutonomousDecisionOutcome.DENY
    assert result.reason_codes == ("global_autonomy_disabled",)


@pytest.mark.parametrize("action", ["stop_service", "restart_service", "reload_service", "reboot", "raw_command"])
def test_v1_hard_allowlist_denies_other_actions(action):
    result = AutonomousRemediationPolicyEvaluator().evaluate(
        context(action_type=action, policy=policy(allowed_action_type=action))
    )
    assert result.outcome is AutonomousDecisionOutcome.DENY
    assert "hard_deny" in result.reason_codes


def test_missing_policy_requires_human_approval():
    result = AutonomousRemediationPolicyEvaluator().evaluate(context(policy=None))
    assert result.outcome is AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL
    assert result.reason_codes == ("no_policy_match",)


def test_ambiguous_policy_match_denies():
    result = AutonomousRemediationPolicyEvaluator().evaluate(context(policy=None, ambiguous_policy_match=True))
    assert result.outcome is AutonomousDecisionOutcome.DENY
    assert result.reason_codes == ("ambiguous_policy_match",)


def test_sandbox_mismatch_and_stale_are_denied():
    mismatch = AutonomousRemediationPolicyEvaluator().evaluate(
        context(sandbox=SimpleNamespace(
            status="passed", plan_id="plan-2", plan_fingerprint="fp-2", server_id=4,
            service="nginx", action_type="start_service", before_evidence_ids=["b"],
            after_evidence_ids=["a"], verification_status="verified", created_at=NOW,
        ))
    )
    assert "sandbox_fingerprint_mismatch" in mismatch.reason_codes

    stale = AutonomousRemediationPolicyEvaluator().evaluate(
        context(sandbox=SimpleNamespace(
            status="passed", plan_id="plan-1", plan_fingerprint="fp-1", server_id=4,
            service="nginx", action_type="start_service", before_evidence_ids=["b"],
            after_evidence_ids=["a"], verification_status="verified",
            created_at=NOW - timedelta(hours=2),
        ), policy=policy(sandbox_max_age_seconds=60))
    )
    assert "sandbox_stale" in stale.reason_codes


def test_insufficient_history_requires_human_approval():
    result = AutonomousRemediationPolicyEvaluator().evaluate(
        context(history=AutonomousHistorySnapshot(
            issue_fingerprint="issue-1", action_type="start_service", target="nginx",
        ))
    )
    assert result.outcome is AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL
    assert "historical_successes_insufficient" in result.reason_codes
