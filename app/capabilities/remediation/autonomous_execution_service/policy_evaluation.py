"""
تنفيذ المعالجة الآلية تحت الحجز والسياسة والتدقيق.

تقيّم الخدمة أهلية التنفيذ، تمنع الحجوزات المتكررة، تستدعي المنفذ المصرح،
وتسجل القرار والنتيجة وحالة التشغيل والتاريخ.
"""
from __future__ import annotations

from sqlalchemy.exc import OperationalError
from uuid import uuid4

from app.core.contracts.autonomous_remediation.autonomous_decision_outcome import AutonomousDecisionOutcome
from app.core.contracts.autonomous_remediation.autonomous_evaluation_context import AutonomousEvaluationContext
from app.core.contracts.autonomous_remediation.autonomous_policy_status import AutonomousPolicyStatus
from app.core.contracts.remediation.remediation_action import RemediationAction
from app.core.contracts.remediation.remediation_plan_status import RemediationPlanStatus
from app.core.policies.autonomous_remediation import AutonomousRemediationPolicyEvaluator
from app.core.utils.datetime import utc_now


class AutonomousPolicyEvaluationHandler:
    """يفصل تقييم السياسة عن دورة التنفيذ الرئيسية."""

    @staticmethod
    def select_policy(matches):
        """يختار سياسة واحدة، أو يرفض المطابقة الغامضة."""
        enabled = []
        inactive = []
        unknown = []
        for policy in matches:
            status = getattr(policy.status, "value", policy.status)
            if status == AutonomousPolicyStatus.ENABLED.value:
                enabled.append(policy)
            elif status in {
                AutonomousPolicyStatus.DISABLED.value,
                AutonomousPolicyStatus.SUSPENDED.value,
            }:
                inactive.append(policy)
            else:
                unknown.append(policy)

        if len(enabled) == 1:
            return enabled[0], False
        if len(enabled) > 1:
            return None, True
        if len(inactive) == 1 and not unknown:
            return inactive[0], False
        if not inactive and not unknown:
            return None, False
        return None, True

    def evaluate(self, service, *, plan_id: str):
        """
        يقيّم خطة المعالجة مقابل السياسة والحالة والأدلة ويصدر قرارًا مسجلًا دون أثر تنفيذي.
        """
        plan = service._remediation_repository.get_plan(plan_id)
        if plan is None:
            raise ValueError("Remediation plan not found.")
        action = service._single_action(plan)
        now = utc_now()
        issue_fingerprint = str((plan.plan_metadata or {}).get("issue_fingerprint") or "")
        matches = service._repository.matching_policies(issue_fingerprint=issue_fingerprint, action_type=action.action_type, target=action.target, server_id=plan.server_id)
        policy_model, ambiguous_policy_match = service._select_policy(matches)
        policy = service._policy_service._model_to_contract(policy_model) if policy_model is not None else None
        history = service._history_service.snapshot(issue_fingerprint=issue_fingerprint, action_type=action.action_type, target=action.target)
        counts = service._repository.execution_counts(policy_id=policy.policy_id, now=now) if policy else {"hour": 0, "day": 0, "last": None}
        runtime = service._repository.get_runtime_state(policy.policy_id) if policy else None
        sandbox = service._remediation_repository.get_latest_sandbox_validation(plan_id)
        reservations = service._repository.list_reservations(plan_id=plan_id, limit=1)
        sandbox_evidence_valid = service._remediation_repository.sandbox_evidence_belongs(
            validation=sandbox,
        ) if sandbox is not None else False
        context = AutonomousEvaluationContext(
            global_enabled=service._automatic_remediation_allowed, now=now, policy=policy,
            plan_id=plan.plan_id, plan_fingerprint=plan.plan_fingerprint or "", issue_fingerprint=issue_fingerprint,
            server_id=plan.server_id, action_type=action.action_type, target=action.target,
            risk=str(plan.risk_level), confidence=float((plan.plan_metadata or {}).get("confidence", 1.0)),
            diagnosis_evidence_valid=bool(plan.diagnosis_claim_ids), plan_evidence_valid=bool(plan.evidence_ids),
            sandbox=sandbox, history=history,
            last_execution_at=counts["last"], hourly_execution_count=counts["hour"], daily_execution_count=counts["day"],
            consecutive_failures=int(runtime.consecutive_failures if runtime else 0),
            execution_completed=False, execution_in_progress=bool(reservations and reservations[0].status in {"reserved", "in_progress"}),
            plan_ready=plan.status in {RemediationPlanStatus.SANDBOX_PASSED.value, RemediationPlanStatus.APPROVED.value},
            ambiguous_policy_match=ambiguous_policy_match,
            sandbox_evidence_valid=sandbox_evidence_valid,
            error_classification=(plan.plan_metadata or {}).get("error_classification"),
        )
        decision = service._evaluator.evaluate(context)
        service._repository.create_decision(decision, history=service._history_dict(history), metadata={"policy_status": policy.status.value if policy else None})
        service._audit(plan_id, "autonomous_policy_evaluated", {
            "decision_id": decision.decision_id, "outcome": decision.outcome.value,
            "reason_codes": list(decision.reason_codes), "policy_id": decision.policy_id,
            "policy_version": decision.policy_version,
        })
        return decision, plan, action, policy, sandbox, history
