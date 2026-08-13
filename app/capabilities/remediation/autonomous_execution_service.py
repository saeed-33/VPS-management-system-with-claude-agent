from __future__ import annotations

from sqlalchemy.exc import OperationalError
from uuid import uuid4

from app.core.contracts.autonomous_remediation import (
    AutonomousDecisionOutcome,
    AutonomousEvaluationContext,
    AutonomousPolicyStatus,
)
from app.core.contracts.remediation import RemediationAction
from app.core.contracts.remediation import RemediationPlanStatus
from app.core.policies.autonomous_remediation import AutonomousRemediationPolicyEvaluator
from app.core.utils.datetime import utc_now


class AutonomousExecutionService:
    """Phase 7 coordinator; all writes remain in RemediationService."""

    def __init__(self, *, repository, remediation_repository, remediation_service, policy_service, history_service, candidate_service, authorization_service, evaluator=None, automatic_remediation_allowed=False):
        self._repository = repository
        self._remediation_repository = remediation_repository
        self._remediation_service = remediation_service
        self._policy_service = policy_service
        self._history_service = history_service
        self._candidate_service = candidate_service
        self._authorization_service = authorization_service
        self._evaluator = evaluator or AutonomousRemediationPolicyEvaluator()
        self._automatic_remediation_allowed = automatic_remediation_allowed

    def evaluate(self, *, plan_id: str):
        plan = self._remediation_repository.get_plan(plan_id)
        if plan is None:
            raise ValueError("Remediation plan not found.")
        action = self._single_action(plan)
        now = utc_now()
        issue_fingerprint = str((plan.plan_metadata or {}).get("issue_fingerprint") or plan.plan_fingerprint or "")
        matches = self._repository.matching_policies(issue_fingerprint=issue_fingerprint, action_type=action.action_type, target=action.target, server_id=plan.server_id)
        policy_model = matches[0] if len(matches) == 1 else None
        policy = self._policy_service._model_to_contract(policy_model) if policy_model is not None else None
        history = self._history_service.snapshot(issue_fingerprint=issue_fingerprint, action_type=action.action_type, target=action.target)
        counts = self._repository.execution_counts(policy_id=policy.policy_id, now=now) if policy else {"hour": 0, "day": 0, "last": None}
        runtime = self._repository.get_runtime_state(policy.policy_id) if policy else None
        sandbox = self._remediation_repository.get_latest_sandbox_validation(plan_id)
        reservations = self._repository.list_reservations(plan_id=plan_id, limit=1)
        sandbox_evidence_valid = self._remediation_repository.sandbox_evidence_belongs(
            validation=sandbox,
        ) if sandbox is not None else False
        context = AutonomousEvaluationContext(
            global_enabled=self._automatic_remediation_allowed, now=now, policy=policy,
            plan_id=plan.plan_id, plan_fingerprint=plan.plan_fingerprint or "", issue_fingerprint=issue_fingerprint,
            server_id=plan.server_id, action_type=action.action_type, target=action.target,
            risk=str(plan.risk_level), confidence=float((plan.plan_metadata or {}).get("confidence", 1.0)),
            diagnosis_evidence_valid=bool(plan.diagnosis_claim_ids), plan_evidence_valid=bool(plan.evidence_ids),
            sandbox=sandbox, history=history,
            last_execution_at=counts["last"], hourly_execution_count=counts["hour"], daily_execution_count=counts["day"],
            consecutive_failures=int(runtime.consecutive_failures if runtime else 0),
            execution_completed=False, execution_in_progress=bool(reservations and reservations[0].status in {"reserved", "in_progress"}),
            plan_ready=plan.status in {RemediationPlanStatus.SANDBOX_PASSED.value, RemediationPlanStatus.APPROVED.value},
            ambiguous_policy_match=len(matches) > 1,
            sandbox_evidence_valid=sandbox_evidence_valid,
        )
        decision = self._evaluator.evaluate(context)
        self._repository.create_decision(decision, history=self._history_dict(history), metadata={"policy_status": policy.status.value if policy else None})
        self._audit(plan_id, "autonomous_policy_evaluated", {
            "decision_id": decision.decision_id, "outcome": decision.outcome.value,
            "reason_codes": list(decision.reason_codes), "policy_id": decision.policy_id,
            "policy_version": decision.policy_version,
        })
        return decision, plan, action, policy, sandbox, history

    def attempt(self, *, plan_id: str, actor: str = "autonomous-policy", idempotency_key: str | None = None):
        decision, plan, action, policy, sandbox, history = self.evaluate(plan_id=plan_id)
        if decision.outcome == AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL:
            if sandbox is None or sandbox.status != "passed":
                return {"outcome": decision.outcome.value, "decision": decision, "approval": None}
            approval = self._remediation_service.request_approval(plan_id=plan_id)
            return {"outcome": decision.outcome.value, "decision": decision, "approval": approval}
        if decision.outcome != AutonomousDecisionOutcome.AUTO_EXECUTE:
            return {"outcome": decision.outcome.value, "decision": decision}

        key = idempotency_key or f"autonomous:{policy.policy_id}:{plan.plan_id}:{plan.plan_fingerprint}:{action.action_type}:{action.target}"
        owner_token = str(uuid4())
        reservation = self._repository.reserve(
            idempotency_key=key, owner_token=owner_token, policy_id=policy.policy_id, plan_id=plan.plan_id,
            plan_fingerprint=plan.plan_fingerprint, action_type=action.action_type, target=action.target,
            server_id=plan.server_id, now=utc_now(),
        )
        self._audit(plan_id, "autonomous_execution_reserved", {
            "reservation_id": reservation.reservation_id, "idempotency_key": reservation.idempotency_key,
            "policy_id": policy.policy_id, "decision_id": decision.decision_id,
        })
        if reservation.status == "completed":
            return {"outcome": decision.outcome.value, "decision": decision, "idempotent": True, "reservation": self._reservation_view(reservation)}
        if reservation.status != "reserved":
            return {"outcome": "in_progress", "decision": decision, "reservation": self._reservation_view(reservation)}

        try:
            authorization = self._authorization_service.issue(decision=decision, sandbox_validation_id=sandbox.validation_id)
            self._audit(plan_id, "autonomous_authorization_issued", {
                "authorization_id": authorization.authorization_id, "decision_id": decision.decision_id,
                "sandbox_validation_id": authorization.sandbox_validation_id,
            })
            self._repository.update_reservation_authorization(reservation.reservation_id, owner_token=owner_token, authorization_id=authorization.authorization_id)
            authorization = self._authorization_service.consume(authorization.authorization_id)
            self._audit(plan_id, "autonomous_authorization_consumed", {"authorization_id": authorization.authorization_id})
            current_plan = self._remediation_repository.get_plan(plan_id)
            current_policy_model = self._repository.get_policy(policy.policy_id)
            current_sandbox = self._remediation_repository.get_sandbox_validation(sandbox.validation_id)
            if current_plan is None or current_plan.plan_fingerprint != authorization.plan_fingerprint:
                raise ValueError("authorization_stale:plan_fingerprint")
            if current_policy_model is None or current_policy_model.version != authorization.policy_version or current_policy_model.status != "enabled":
                raise ValueError("authorization_stale:policy_version")
            if current_sandbox is None or current_sandbox.plan_fingerprint != authorization.plan_fingerprint or current_sandbox.status != "passed":
                raise ValueError("authorization_stale:sandbox")
            if (current_sandbox.server_id, current_sandbox.action_type, current_sandbox.service) != (
                authorization.server_id, authorization.action_type, authorization.target
            ) or current_sandbox.validation_id != authorization.sandbox_validation_id:
                raise ValueError("authorization_stale:binding")
            outcome = self._remediation_service.apply_approved(
                plan_id=plan.plan_id, server_id=plan.server_id, actor=actor,
                idempotency_key=key, autonomous_authorization=authorization,
            )
            if not outcome.get("applied") and outcome.get("execution_id"):
                rollback = self._remediation_service.rollback(plan_id=plan.plan_id, execution_id=outcome["execution_id"], actor=actor, server_id=plan.server_id)
                outcome["autonomous_rollback"] = rollback
            success = bool(outcome.get("applied"))
            self._repository.finalize_reservation(reservation.reservation_id, owner_token=owner_token, status="completed" if success else "failed", execution_id=outcome.get("execution_id"))
            self._record_runtime(policy, decision, success, outcome.get("execution_id"))
            self._audit(plan_id, "autonomous_execution_finalized", {
                "reservation_id": reservation.reservation_id, "execution_id": outcome.get("execution_id"),
                "success": success,
            })
            return {"outcome": "auto_execute", "decision": decision, "authorization_id": authorization.authorization_id, "result": outcome}
        except Exception as exc:
            self._repository.finalize_reservation(reservation.reservation_id, owner_token=owner_token, status="failed")
            self._record_runtime(policy, decision, False, None)
            self._audit(plan_id, "autonomous_execution_failed", {
                "reservation_id": reservation.reservation_id, "error": str(exc),
            })
            return {"outcome": "deny", "decision": decision, "authorization_id": locals().get("authorization", None).authorization_id if locals().get("authorization") else None, "error": str(exc)}

    def candidates(self):
        return self._candidate_service.list_candidates()

    def list_decisions(self, *, plan_id: str | None = None, limit: int = 100):
        return self._repository.list_decisions(plan_id=plan_id, limit=min(max(limit, 1), 500))

    def get_decision(self, decision_id: str):
        return self._repository.get_decision(decision_id)

    def list_reservations(self, *, policy_id: str | None = None, plan_id: str | None = None, limit: int = 100):
        return self._repository.list_reservations(policy_id=policy_id, plan_id=plan_id, limit=min(max(limit, 1), 500))

    def runtime_state(self, policy_id: str):
        return self._repository.get_runtime_state(policy_id)

    def history(self, *, issue_fingerprint: str, action_type: str, target: str):
        return self._history_service.snapshot(issue_fingerprint=issue_fingerprint, action_type=action_type, target=target)

    def _audit(self, plan_id: str, event_type: str, payload: dict) -> None:
        try:
            self._remediation_service.audit_autonomous(plan_id=plan_id, event_type=event_type, payload=payload)
        except (OperationalError, ValueError):
            return

    @staticmethod
    def _reservation_view(reservation) -> dict:
        return {
            "reservation_id": reservation.reservation_id,
            "idempotency_key": reservation.idempotency_key,
            "status": reservation.status,
            "policy_id": reservation.policy_id,
            "plan_id": reservation.plan_id,
            "authorization_id": reservation.authorization_id,
            "execution_id": reservation.execution_id,
        }

    def _record_runtime(self, policy, decision, success: bool, execution_id: str | None):
        current = self._repository.get_runtime_state(policy.policy_id)
        failures = 0 if success else int(current.consecutive_failures) + 1
        updates = {"last_execution_at": utc_now(), "consecutive_failures": failures}
        if not success and policy.auto_suspend_on_failure:
            updates.update({"suspended_at": utc_now(), "suspension_reason": "execution_failure", "triggering_execution_id": execution_id, "triggering_decision_id": decision.decision_id})
            self._policy_service.suspend(policy.policy_id, reason="execution_failure")
        self._repository.update_runtime_state(policy.policy_id, **updates)

    @staticmethod
    def _single_action(plan):
        actions = [RemediationAction.from_dict(item) for item in (plan.proposed_actions or [])]
        if len(actions) != 1:
            raise ValueError("Phase 7 requires exactly one registered action.")
        return actions[0]

    @staticmethod
    def _history_dict(history):
        return {"issue_fingerprint": history.issue_fingerprint, "action_type": history.action_type, "target": history.target,
                "supervised_execution_count": history.supervised_execution_count, "verified_success_count": history.verified_success_count,
                "failed_execution_count": history.failed_execution_count, "rollback_failure_count": history.rollback_failure_count,
                "success_rate": history.success_rate, "failure_rate": history.failure_rate}
