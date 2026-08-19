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


class AutonomousAttemptHandler:
    """ينفذ محاولة المعالجة الآلية مع الحجز وإعادة التشغيل الآمن."""

    def attempt(self, service, *, plan_id: str, actor: str = "autonomous-policy", idempotency_key: str | None = None):
        """
        ينفذ قرارًا آليًا مصرحًا مع حجز يمنع التكرار ثم يسجل النتيجة والتحقق.
        """
        plan = service._remediation_repository.get_plan(plan_id)
        if plan is None:
            raise ValueError("Remediation plan not found.")
        action = service._single_action(plan)

        existing = None
        if idempotency_key is not None:
            existing = service._repository.get_reservation_by_idempotency_key(idempotency_key)
            if existing is not None and not service._reservation_lease_stale(existing, now=utc_now()):
                return service._replay_existing_reservation(
                    existing=existing, plan=plan, action=action, idempotency_key=idempotency_key,
                )
        stale_existing = existing if existing is not None and service._reservation_lease_stale(existing, now=utc_now()) else None

        decision, plan, action, policy, sandbox, history = service.evaluate(plan_id=plan_id)
        if decision.outcome == AutonomousDecisionOutcome.REQUIRE_HUMAN_APPROVAL:
            if sandbox is None or sandbox.status != "passed":
                return {"outcome": decision.outcome.value, "decision": decision, "approval": None}
            approval = service._remediation_service.request_approval(plan_id=plan_id)
            return {"outcome": decision.outcome.value, "decision": decision, "approval": approval}
        if decision.outcome != AutonomousDecisionOutcome.AUTO_EXECUTE:
            return {"outcome": decision.outcome.value, "decision": decision}

        key = idempotency_key or f"autonomous:{policy.policy_id}:{plan.plan_id}:{plan.plan_fingerprint}:{action.action_type}:{action.target}"
        if stale_existing is None:
            candidate = service._repository.get_reservation_by_idempotency_key(key)
            if candidate is not None and service._reservation_lease_stale(candidate, now=utc_now()):
                stale_existing = candidate
        owner_token = str(uuid4())
        reservation = service._repository.reserve(
            idempotency_key=key, owner_token=owner_token, policy_id=policy.policy_id, plan_id=plan.plan_id,
            plan_fingerprint=plan.plan_fingerprint, action_type=action.action_type, target=action.target,
            server_id=plan.server_id, now=utc_now(),
        )
        if not service._reservation_matches(
            reservation=reservation, plan=plan, action=action, idempotency_key=key,
        ):
            return {
                "outcome": "deny",
                "error": "idempotency_reservation_binding_mismatch",
                "reservation": service._reservation_view(reservation),
            }
        if stale_existing is not None:
            service._audit(plan_id, "autonomous_reservation_recovered", {
                "reservation_id": reservation.reservation_id,
                "idempotency_key": reservation.idempotency_key,
                "owner_token_replaced": reservation.owner_token == owner_token,
                "authorization_id": reservation.authorization_id,
                "execution_id": reservation.execution_id,
            })
        service._audit(plan_id, "autonomous_execution_reserved", {
            "reservation_id": reservation.reservation_id, "idempotency_key": reservation.idempotency_key,
            "policy_id": policy.policy_id, "decision_id": decision.decision_id,
        })
        if reservation.status == "completed":
            return service._replay_existing_reservation(
                existing=reservation, plan=plan, action=action, idempotency_key=key,
                decision=decision,
            )
        if reservation.status == "failed":
            if stale_existing is not None:
                runtime = service._record_runtime(
                    policy, decision, False, reservation.execution_id,
                    failure_key=reservation.execution_id or reservation.reservation_id,
                )
                service._audit(plan_id, "autonomous_execution_failed", {
                    "reservation_id": reservation.reservation_id,
                    "execution_id": reservation.execution_id,
                    "recovered": True,
                    "consecutive_failures": getattr(runtime, "consecutive_failures", None),
                })
            return {
                "outcome": "deny",
                "decision": decision,
                "error": "idempotency_reservation_not_replayable",
                "reservation": service._reservation_view(reservation),
            }
        if reservation.status != "reserved":
            return {
                "outcome": "in_progress", "idempotent": True,
                "decision": decision, "reservation": service._reservation_view(reservation),
            }

        try:
            authorization = None
            if reservation.authorization_id:
                loader = getattr(service._authorization_service, "get", None)
                if loader is None:
                    raise ValueError("authorization_stale:recovery_loader_missing")
                authorization = loader(reservation.authorization_id)
                if authorization.status != "valid":
                    raise ValueError("authorization_stale:recovery")
            else:
                authorization = service._authorization_service.issue(decision=decision, sandbox_validation_id=sandbox.validation_id)
                service._audit(plan_id, "autonomous_authorization_issued", {
                    "authorization_id": authorization.authorization_id, "decision_id": decision.decision_id,
                    "sandbox_validation_id": authorization.sandbox_validation_id,
                })
                service._repository.update_reservation_authorization(reservation.reservation_id, owner_token=owner_token, authorization_id=authorization.authorization_id)
            authorization = service._authorization_service.consume(authorization.authorization_id)
            service._audit(plan_id, "autonomous_authorization_consumed", {"authorization_id": authorization.authorization_id})
            current_plan = service._remediation_repository.get_plan(plan_id)
            current_policy_model = service._repository.get_policy(policy.policy_id)
            current_sandbox = service._remediation_repository.get_sandbox_validation(sandbox.validation_id)
            if current_plan is None or (
                authorization.policy_id != decision.policy_id
                or authorization.policy_version != decision.policy_version
                or authorization.decision_id != decision.decision_id
                or authorization.plan_id != current_plan.plan_id
                or authorization.plan_fingerprint != current_plan.plan_fingerprint
                or authorization.server_id != current_plan.server_id
                or authorization.action_type != action.action_type
                or authorization.target != action.target
            ):
                raise ValueError("authorization_stale:binding")
            if (
                current_policy_model is None
                or current_policy_model.policy_id != authorization.policy_id
                or current_policy_model.version != authorization.policy_version
                or current_policy_model.status != "enabled"
            ):
                raise ValueError("authorization_stale:policy_version")
            if current_sandbox is None or current_sandbox.plan_fingerprint != authorization.plan_fingerprint or current_sandbox.status != "passed":
                raise ValueError("authorization_stale:sandbox")
            if (current_sandbox.server_id, current_sandbox.action_type, current_sandbox.service) != (
                authorization.server_id, authorization.action_type, authorization.target
            ) or current_sandbox.validation_id != authorization.sandbox_validation_id:
                raise ValueError("authorization_stale:binding")
            # لا تكفي الموافقة النظرية: نعيد فحص أن الخطة والاختبار والسياسة
            # تخص الحالة نفسها قبل أي تغيير فعلي.
            outcome = service._remediation_service.apply_approved(
                plan_id=plan.plan_id, server_id=plan.server_id, actor=actor,
                idempotency_key=key, autonomous_authorization=authorization,
            )
            if not outcome.get("applied") and outcome.get("execution_id"):
                rollback = service._remediation_service.rollback(plan_id=plan.plan_id, execution_id=outcome["execution_id"], actor=actor, server_id=plan.server_id)
                outcome["autonomous_rollback"] = rollback
            success = bool(outcome.get("applied"))
            # يمنع الحجز تكرار التغيير نفسه، ثم تحفظ النتيجة ما حدث حتى يمكن
            # تدقيقه أو التراجع عنه.
            service._repository.finalize_reservation(reservation.reservation_id, owner_token=owner_token, status="completed" if success else "failed", execution_id=outcome.get("execution_id"))
            service._record_runtime(
                policy, decision, success, outcome.get("execution_id"),
                failure_key=outcome.get("execution_id") or reservation.reservation_id,
            )
            service._audit(plan_id, "autonomous_execution_finalized", {
                "reservation_id": reservation.reservation_id, "execution_id": outcome.get("execution_id"),
                "success": success,
            })
            if not success:
                service._audit(plan_id, "autonomous_execution_failed", {
                    "reservation_id": reservation.reservation_id,
                    "execution_id": outcome.get("execution_id"),
                    "blocked_reason": outcome.get("blocked_reason"),
                    "rollback": outcome.get("autonomous_rollback"),
                })
            return {"outcome": "auto_execute", "decision": decision, "authorization_id": authorization.authorization_id, "result": outcome}
        except Exception as exc:
            service._repository.finalize_reservation(reservation.reservation_id, owner_token=owner_token, status="failed")
            service._record_runtime(
                policy, decision, False, None,
                failure_key=reservation.reservation_id,
            )
            service._audit(plan_id, "autonomous_execution_failed", {
                "reservation_id": reservation.reservation_id, "error": str(exc),
            })
            return {"outcome": "deny", "decision": decision, "authorization_id": locals().get("authorization", None).authorization_id if locals().get("authorization") else None, "error": str(exc)}
