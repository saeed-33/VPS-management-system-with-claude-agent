from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.capabilities.remediation.autonomous_execution_service import (
    AutonomousExecutionService,
)
from app.core.contracts.autonomous_remediation import (
    AutonomousDecisionOutcome,
    AutonomousEvaluationContext,
    AutonomousHistorySnapshot,
    AutonomousPolicyStatus,
    AutonomousRemediationPolicy,
)
from app.core.contracts.remediation import RemediationPlanStatus
from app.core.policies.autonomous_remediation import (
    AutonomousRemediationPolicyEvaluator,
)
from app.interfaces.mcp.registry import ProjectMcpToolBoundary


NOW = datetime(2026, 8, 14, tzinfo=timezone.utc)


def policy(**updates):
    values = {
        "policy_id": "policy-1",
        "name": "Start nginx",
        "description": "negative security fixture",
        "status": AutonomousPolicyStatus.ENABLED,
        "version": 1,
        "issue_fingerprint": "issue-1",
        "allowed_action_type": "start_service",
        "allowed_target_pattern": "nginx",
        "minimum_success_count": 1,
        "maximum_failure_rate": 0.0,
        "maximum_rollback_failure_rate": 0.0,
        "allowed_server_ids": (4,),
    }
    values.update(updates)
    return AutonomousRemediationPolicy(**values)


def sandbox(**updates):
    values = {
        "validation_id": "sandbox-1",
        "status": "passed",
        "plan_id": "plan-1",
        "plan_fingerprint": "plan-fp-1",
        "server_id": 4,
        "service": "nginx",
        "action_type": "start_service",
        "before_evidence_ids": ["before"],
        "after_evidence_ids": ["after"],
        "verification_status": "verified",
        "created_at": NOW,
    }
    values.update(updates)
    return SimpleNamespace(**values)


def history(**updates):
    values = {
        "issue_fingerprint": "issue-1",
        "action_type": "start_service",
        "target": "nginx",
        "supervised_execution_count": 1,
        "successful_execution_count": 1,
        "verified_success_count": 1,
    }
    values.update(updates)
    return AutonomousHistorySnapshot(**values)


def context(**updates):
    values = {
        "global_enabled": True,
        "now": NOW,
        "policy": policy(),
        "plan_id": "plan-1",
        "plan_fingerprint": "plan-fp-1",
        "issue_fingerprint": "issue-1",
        "server_id": 4,
        "action_type": "start_service",
        "target": "nginx",
        "risk": "low",
        "confidence": 0.95,
        "diagnosis_evidence_valid": True,
        "plan_evidence_valid": True,
        "sandbox": sandbox(),
        "sandbox_evidence_valid": True,
        "history": history(),
        "plan_ready": True,
    }
    values.update(updates)
    return AutonomousEvaluationContext(**values)


def evaluate(**updates):
    return AutonomousRemediationPolicyEvaluator().evaluate(context(**updates))


def assert_denied(result, reason: str | None = None):
    assert result.outcome is AutonomousDecisionOutcome.DENY
    if reason is not None:
        assert reason in result.reason_codes


@pytest.mark.parametrize(
    ("updates", "reason"),
    [
        ({"global_enabled": False}, "global_autonomy_disabled"),
        ({"policy": policy(status=AutonomousPolicyStatus.DISABLED)}, "policy_disabled"),
        ({"policy": policy(status=AutonomousPolicyStatus.SUSPENDED)}, "policy_suspended"),
        ({
            "policy": None,
            "ambiguous_policy_match": True,
        }, "ambiguous_policy_match"),
    ],
)
def test_global_and_policy_selection_gates_fail_closed(updates, reason):
    assert_denied(evaluate(**updates), reason)


class SecurityRepository:
    def __init__(self, policies):
        self.policies = list(policies)
        self.decisions = []
        self.audit = []
        self.reserve_calls = 0

    def matching_policies(self, **_kwargs):
        return self.policies

    def execution_counts(self, **_kwargs):
        return {"hour": 0, "day": 0, "last": None}

    def get_runtime_state(self, policy_id):
        return SimpleNamespace(policy_id=policy_id, consecutive_failures=0)

    def list_reservations(self, **_kwargs):
        return []

    def create_decision(self, decision, **_kwargs):
        self.decisions.append(decision)

    def get_policy(self, policy_id):
        return next((item for item in self.policies if item.policy_id == policy_id), None)

    def reserve(self, **_kwargs):
        self.reserve_calls += 1
        raise AssertionError("A negative decision must not create a reservation.")


class SecurityRemediationRepository:
    def __init__(self, plan):
        self.plan = plan
        self.sandbox = sandbox()

    def get_plan(self, plan_id):
        return self.plan if plan_id == self.plan.plan_id else None

    def get_latest_sandbox_validation(self, _plan_id):
        return self.sandbox

    def sandbox_evidence_belongs(self, **_kwargs):
        return True


class SecurityRemediationService:
    def __init__(self):
        self.apply_calls = 0
        self.approval_calls = 0

    def audit_autonomous(self, **kwargs):
        self.audit.append(kwargs)

    def request_approval(self, **_kwargs):
        self.approval_calls += 1
        return SimpleNamespace()

    def apply_approved(self, **_kwargs):
        self.apply_calls += 1
        raise AssertionError("A negative decision must not execute remediation.")


class SecurityAuthorizationService:
    def __init__(self):
        self.issue_calls = 0

    def issue(self, **_kwargs):
        self.issue_calls += 1
        raise AssertionError("A negative decision must not issue authorization.")


def make_operational_service(*, policies, automatic_remediation_allowed=True):
    plan = SimpleNamespace(
        plan_id="plan-1",
        plan_fingerprint="plan-fp-1",
        server_id=4,
        status=RemediationPlanStatus.SANDBOX_PASSED.value,
        plan_metadata={"issue_fingerprint": "issue-1"},
        risk_level="low",
        diagnosis_claim_ids=["claim-1"],
        evidence_ids=["evidence-1"],
        proposed_actions=[{
            "id": "start-nginx",
            "action_type": "start_service",
            "target": "nginx",
        }],
    )
    repository = SecurityRepository(policies)
    remediation_repository = SecurityRemediationRepository(plan)
    remediation_service = SecurityRemediationService()
    authorization_service = SecurityAuthorizationService()
    remediation_service.audit = repository.audit
    service = AutonomousExecutionService(
        repository=repository,
        remediation_repository=remediation_repository,
        remediation_service=remediation_service,
        policy_service=SimpleNamespace(_model_to_contract=lambda model: model),
        history_service=SimpleNamespace(snapshot=lambda **kwargs: history(**kwargs)),
        candidate_service=SimpleNamespace(),
        authorization_service=authorization_service,
        automatic_remediation_allowed=automatic_remediation_allowed,
    )
    return service, repository, remediation_service, authorization_service


@pytest.mark.parametrize(
    ("policies", "automatic", "reason"),
    [
        ([policy()], False, "global_autonomy_disabled"),
        ([policy(status=AutonomousPolicyStatus.DISABLED)], True, "policy_disabled"),
        ([policy(status=AutonomousPolicyStatus.SUSPENDED)], True, "policy_suspended"),
        ([policy(), policy(policy_id="policy-2")], True, "ambiguous_policy_match"),
    ],
)
def test_service_negative_gates_create_no_execution_side_effects(policies, automatic, reason):
    service, repository, remediation, authorization = make_operational_service(
        policies=policies,
        automatic_remediation_allowed=automatic,
    )

    result = service.attempt(plan_id="plan-1")

    assert result["outcome"] == "deny"
    assert reason in result["decision"].reason_codes
    assert repository.reserve_calls == 0
    assert authorization.issue_calls == 0
    assert remediation.apply_calls == 0


def test_denial_is_persisted_and_audited():
    service, repository, _remediation, _authorization = make_operational_service(
        policies=[policy()], automatic_remediation_allowed=False,
    )

    decision, *_ = service.evaluate(plan_id="plan-1")

    assert decision.outcome is AutonomousDecisionOutcome.DENY
    assert repository.decisions[0].decision_id == decision.decision_id
    assert repository.audit[0]["event_type"] == "autonomous_policy_evaluated"
    assert repository.audit[0]["payload"]["reason_codes"] == ["global_autonomy_disabled"]


def test_missing_fingerprint_requires_human_approval_and_never_uses_plan_fingerprint():
    result = evaluate(issue_fingerprint="", plan_fingerprint="trusted-looking-plan-fp")

    assert result.outcome is AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL
    assert result.reason_codes == ("issue_fingerprint_missing",)


def test_issue_fingerprint_mismatch_cannot_auto_execute():
    result = evaluate(
        issue_fingerprint="issue-2",
        policy=policy(issue_fingerprint="issue-1"),
    )

    assert result.outcome is not AutonomousDecisionOutcome.AUTO_EXECUTE


@pytest.mark.parametrize(
    ("updates", "reason"),
    [
        ({"server_id": 9}, "server_not_allowed"),
        ({"target": "redis"}, "target_not_allowed"),
            ({"action_type": "stop_service"}, "hard_deny"),
    ],
)
def test_policy_scope_mismatches_fail_closed(updates, reason):
    assert_denied(evaluate(**updates), reason)


@pytest.mark.parametrize(
    "action_type",
    [
        "stop_service", "reboot", "firewall_change", "package_install",
        "filesystem_repair", "restart_database", "arbitrary_shell", "raw_ssh", "raw_sql",
    ],
)
def test_hard_v1_allowlist_rejects_dangerous_actions(action_type):
    result = evaluate(
        action_type=action_type,
        policy=policy(allowed_action_type=action_type),
    )
    assert_denied(result, "hard_deny")


@pytest.mark.parametrize("risk", ["medium", "high", "critical"])
def test_risk_ceiling_rejects_non_low_risk(risk):
    assert_denied(evaluate(risk=risk), "risk_too_high")


@pytest.mark.parametrize(
    ("updates", "reason"),
    [
        ({"sandbox": None}, "sandbox_missing"),
        ({"sandbox": sandbox(status="failed")}, "sandbox_failed"),
        ({"sandbox": sandbox(created_at=NOW - timedelta(hours=2)), "policy": policy(sandbox_max_age_seconds=60)}, "sandbox_stale"),
        ({"sandbox": sandbox(plan_fingerprint="other")}, "sandbox_fingerprint_mismatch"),
        ({"sandbox": sandbox(plan_id="other")}, "sandbox_fingerprint_mismatch"),
        ({"sandbox": sandbox(server_id=9)}, "target_not_allowed"),
        ({"sandbox": sandbox(action_type="stop_service")}, "target_not_allowed"),
        ({"sandbox": sandbox(service="redis")}, "target_not_allowed"),
        ({"sandbox": sandbox(before_evidence_ids=[])}, "evidence_incomplete"),
        ({"sandbox": sandbox(after_evidence_ids=[])}, "evidence_incomplete"),
        ({"sandbox": sandbox(verification_status="failed")}, "evidence_incomplete"),
        ({"sandbox_evidence_valid": False}, "evidence_incomplete"),
    ],
)
def test_sandbox_required_fresh_and_bound(updates, reason):
    assert_denied(evaluate(**updates), reason)


@pytest.mark.parametrize(
    "updates",
    [
        {"diagnosis_evidence_valid": False},
        {"plan_evidence_valid": False},
    ],
)
def test_diagnosis_and_plan_evidence_are_required(updates):
    assert_denied(evaluate(**updates), "evidence_incomplete")


def test_rollback_capability_is_required():
    assert_denied(evaluate(policy=policy(rollback_required=False)), "rollback_unavailable")


def test_insufficient_history_falls_back_to_human_approval():
    result = evaluate(history=history(verified_success_count=0, supervised_execution_count=0))
    assert result.outcome is AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL
    assert "historical_successes_insufficient" in result.reason_codes


@pytest.mark.parametrize(
    "updates",
    [
        {"history": history(failed_execution_count=1, supervised_execution_count=2)},
        {"history": history(rollback_required_count=2, rollback_failure_count=1)},
    ],
)
def test_history_failure_ceilings_deny(updates):
    assert_denied(evaluate(**updates), "historical_failure_rate_too_high")


@pytest.mark.parametrize(
    "updates",
    [
        {"hourly_execution_count": 1},
        {"daily_execution_count": 3},
        {"last_execution_at": NOW - timedelta(seconds=1), "policy": policy(cooldown_seconds=60)},
        {"consecutive_failures": 1},
    ],
)
def test_runtime_limits_deny_without_a_new_execution(updates):
    result = evaluate(**updates)
    assert_denied(result)
    assert result.outcome is not AutonomousDecisionOutcome.AUTO_EXECUTE


def test_authorization_binding_rejects_every_immutable_field_change():
    from tests.test_autonomous_execution_idempotency import make_service

    immutable_fields = {
        "policy_id": "other-policy",
        "policy_version": 2,
        "decision_id": "other-decision",
        "plan_id": "other-plan",
        "plan_fingerprint": "other-fingerprint",
        "server_id": 9,
        "action_type": "stop_service",
        "target": "redis",
        "sandbox_validation_id": "other-sandbox",
    }
    for field, value in immutable_fields.items():
        service, _reservations, remediation, authorization, _repository = make_service()
        original_consume = authorization.consume

        def consume(authorization_id, *, _original=original_consume, _field=field, _value=value):
            issued = _original(authorization_id)
            setattr(issued, _field, _value)
            return issued

        authorization.consume = consume
        result = service.attempt(plan_id="plan-1", idempotency_key=f"binding-{field}")

        assert result["outcome"] == "deny", field
        assert result["error"] == "authorization_stale:binding", field
        assert remediation.apply_calls == 0, field


def test_claude_mcp_surface_cannot_bypass_phase7_safety_gates():
    boundary = ProjectMcpToolBoundary(
        server_service=None,
        monitoring_profile_service=None,
        monitoring_service=None,
        report_query_service=None,
    )
    definitions = {item.tool_id: item for item in boundary.list_tools()}
    autonomous = definitions["attempt_autonomous_remediation"]

    assert autonomous.input_schema == {
        "type": "object",
        "properties": {"plan_id": {"type": "string"}},
        "required": ["plan_id"],
        "additionalProperties": False,
    }
    serialized = json.dumps(
        [
            {
                "tool_id": item.tool_id,
                "description": item.description,
                "input_schema": item.input_schema,
            }
            for item in definitions.values()
        ],
        sort_keys=True,
    ).lower()
    for forbidden in (
        "enable_policy", "resume_policy", "force_execute", "raw_ssh", "raw_sql",
        "unrestricted_shell", "arbitrary_command", "automatic_remediation_allowed",
    ):
        assert forbidden not in serialized

    assert not {
        "enable_autonomy", "create_policy", "enable_policy", "resume_policy",
        "force_execution", "raw_ssh", "raw_sql", "unrestricted_shell",
    } & definitions.keys()


def test_mcp_autonomous_attempt_only_forwards_bounded_plan_identity():
    calls = []

    class AutonomousSpy:
        def attempt(self, **kwargs):
            calls.append(kwargs)
            return {"outcome": "deny"}

    boundary = ProjectMcpToolBoundary(
        server_service=None,
        monitoring_profile_service=None,
        monitoring_service=None,
        report_query_service=None,
        autonomous_execution_service=AutonomousSpy(),
    )
    result = asyncio.run(boundary.execute(SimpleNamespace(
        tool_id="attempt_autonomous_remediation",
        arguments={
            "plan_id": "plan-1",
            "raw_ssh": "rm -rf /",
            "raw_sql": "DROP TABLE secrets",
        },
    )))

    assert result.success is False
    assert calls == [{"plan_id": "plan-1", "actor": "claude-autonomous-policy"}]
