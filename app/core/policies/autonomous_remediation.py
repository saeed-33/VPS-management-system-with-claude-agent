from __future__ import annotations

import fnmatch
from datetime import timedelta

from app.core.contracts.autonomous_remediation import (
    AutonomousDecisionOutcome,
    AutonomousDecisionReasonCode as Code,
    AutonomousEvaluationContext,
    AutonomousPolicyStatus,
    V1_AUTONOMOUS_ACTIONS,
    V1_AUTONOMOUS_RISK_CEILING,
)


class AutonomousRemediationPolicyEvaluator:
    """Pure Phase 7 V1 eligibility evaluator; it never executes or persists."""

    def evaluate(self, context: AutonomousEvaluationContext):
        reasons: list[str] = []
        messages: list[str] = []
        policy = context.policy

        def deny(code: Code, message: str):
            reasons.append(code.value)
            messages.append(message)
            return self._decision(context, AutonomousDecisionOutcome.DENY, reasons, messages)

        if not context.global_enabled:
            return deny(Code.GLOBAL_AUTONOMY_DISABLED, "Global autonomous remediation is disabled.")
        if not context.issue_fingerprint:
            reasons.append(Code.ISSUE_FINGERPRINT_MISSING.value)
            messages.append("A trusted persisted issue fingerprint is required; supervised remediation remains available.")
            return self._decision(context, AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL, reasons, messages)
        if context.execution_completed:
            return deny(Code.EXECUTION_ALREADY_COMPLETED, "This autonomous operation already has a terminal execution.")
        if context.execution_in_progress:
            return deny(Code.EXECUTION_IN_PROGRESS, "This autonomous operation is already reserved.")
        if not context.plan_ready:
            return deny(Code.HARD_DENY, "The remediation plan is not in an executable state.")
        if context.action_type not in V1_AUTONOMOUS_ACTIONS:
            return deny(Code.HARD_DENY, "The action is outside the Phase 7 V1 hard allowlist.")
        if context.risk != V1_AUTONOMOUS_RISK_CEILING:
            return deny(Code.RISK_TOO_HIGH, "Only low-risk autonomous remediation is permitted.")
        if context.sandbox is None:
            return deny(Code.SANDBOX_MISSING, "A current passed sandbox validation is required.")
        if context.sandbox.status != "passed":
            return deny(Code.SANDBOX_FAILED, "Sandbox validation did not pass.")
        if policy is None:
            if context.ambiguous_policy_match:
                return deny(Code.AMBIGUOUS_POLICY_MATCH, "Multiple autonomous policies match; autonomy is denied until an operator resolves the ambiguity.")
            return self._decision(context, AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL, (Code.NO_POLICY_MATCH.value,), ("No matching autonomous policy exists.",))
        if policy.status == AutonomousPolicyStatus.DISABLED:
            return deny(Code.POLICY_DISABLED, "The matching autonomous policy is disabled.")
        if policy.status == AutonomousPolicyStatus.SUSPENDED:
            return deny(Code.POLICY_SUSPENDED, "The matching autonomous policy is suspended.")
        if policy.allowed_action_type != context.action_type:
            return deny(Code.ACTION_NOT_AUTONOMOUS_ALLOWLISTED, "The policy action does not match the requested action.")
        if not fnmatch.fnmatchcase(context.target, policy.allowed_target_pattern):
            return deny(Code.TARGET_NOT_ALLOWED, "The target is outside the policy allowlist.")
        if policy.allowed_server_ids and context.server_id not in policy.allowed_server_ids:
            return deny(Code.SERVER_NOT_ALLOWED, "The server is outside the policy allowlist.")
        if policy.issue_fingerprint != context.issue_fingerprint:
            return deny(Code.TARGET_NOT_ALLOWED, "The issue fingerprint does not match the policy.")
        if context.confidence < policy.minimum_confidence:
            reasons.append(Code.CONFIDENCE_INSUFFICIENT.value)
            messages.append("Diagnosis confidence is below the policy threshold.")
            return self._decision(context, AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL, reasons, messages)
        if not context.diagnosis_evidence_valid or not context.plan_evidence_valid:
            return deny(Code.EVIDENCE_INCOMPLETE, "Persisted diagnosis and plan Evidence links are required.")
        sandbox = context.sandbox
        if not policy.sandbox_required or sandbox is None:
            return deny(Code.SANDBOX_MISSING, "A current passed sandbox validation is required.")
        if sandbox.status != "passed":
            return deny(Code.SANDBOX_FAILED, "Sandbox validation did not pass.")
        if sandbox.plan_id != context.plan_id:
            return deny(Code.SANDBOX_FINGERPRINT_MISMATCH, "Sandbox validation belongs to another plan.")
        if sandbox.plan_fingerprint != context.plan_fingerprint:
            return deny(Code.SANDBOX_FINGERPRINT_MISMATCH, "Sandbox validation is bound to another plan fingerprint.")
        if sandbox.server_id != context.server_id or sandbox.service != context.target or sandbox.action_type != context.action_type:
            return deny(Code.TARGET_NOT_ALLOWED, "Sandbox target binding does not match the requested operation.")
        if not sandbox.before_evidence_ids or not sandbox.after_evidence_ids or sandbox.verification_status != "verified" or not context.sandbox_evidence_valid:
            return deny(Code.EVIDENCE_INCOMPLETE, "Sandbox Before/After Evidence and verification are required.")
        if context.now - sandbox.created_at > timedelta(seconds=policy.sandbox_max_age_seconds):
            return deny(Code.SANDBOX_STALE, "Sandbox validation is stale.")
        if policy.rollback_required is False:
            return deny(Code.ROLLBACK_UNAVAILABLE, "Autonomous remediation requires restoration capability.")
        if context.history.verified_success_count < max(1, policy.minimum_success_count):
            reasons.append(Code.HISTORICAL_SUCCESSES_INSUFFICIENT.value)
            messages.append("Historical verified successes are below the policy threshold.")
            return self._decision(context, AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL, reasons, messages)
        if context.history.failure_rate > policy.maximum_failure_rate:
            return deny(Code.HISTORICAL_FAILURE_RATE_TOO_HIGH, "Historical failure rate exceeds the policy ceiling.")
        if context.history.rollback_failure_rate > policy.maximum_rollback_failure_rate:
            return deny(Code.HISTORICAL_FAILURE_RATE_TOO_HIGH, "Historical rollback failure rate exceeds the policy ceiling.")
        if context.last_execution_at and context.now - context.last_execution_at < timedelta(seconds=policy.cooldown_seconds):
            return deny(Code.COOLDOWN_ACTIVE, "Policy cooldown is active.")
        if context.hourly_execution_count >= policy.max_executions_per_hour:
            return deny(Code.HOURLY_RATE_LIMIT_EXCEEDED, "Policy hourly rate limit is reached.")
        if context.daily_execution_count >= policy.max_executions_per_day:
            return deny(Code.DAILY_RATE_LIMIT_EXCEEDED, "Policy daily rate limit is reached.")
        if context.consecutive_failures >= policy.max_consecutive_failures:
            return deny(Code.CONSECUTIVE_FAILURE_LIMIT_EXCEEDED, "Policy consecutive failure limit is reached.")

        reasons.append(Code.POLICY_MATCH.value)
        messages.append("All deterministic autonomous remediation gates passed.")
        return self._decision(context, AutonomousDecisionOutcome.AUTO_EXECUTE, reasons, messages)

    @staticmethod
    def _decision(context, outcome, reasons, messages):
        from app.core.contracts.autonomous_remediation import AutonomousPolicyDecision
        from uuid import uuid4
        return AutonomousPolicyDecision(
            decision_id=str(uuid4()), outcome=outcome,
            reason_codes=tuple(reasons), human_readable_reasons=tuple(messages),
            policy_id=context.policy.policy_id if context.policy else None,
            policy_version=context.policy.version if context.policy else None,
            plan_id=context.plan_id, plan_fingerprint=context.plan_fingerprint,
            issue_fingerprint=context.issue_fingerprint, server_id=context.server_id,
            action_type=context.action_type, target=context.target,
            evaluated_at=context.now,
        )
