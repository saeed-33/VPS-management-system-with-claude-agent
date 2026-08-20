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
from app.core.ports.remediation.autonomous_remediation_repository import AutonomousRemediationRepositoryPort
from app.core.ports.remediation.remediation_repository import RemediationRepositoryPort
from app.core.utils.datetime import utc_now


from .policy_evaluation import AutonomousPolicyEvaluationHandler
from .attempt_handler import AutonomousAttemptHandler
from .runtime_recorder import AutonomousRuntimeRecorder

class AutonomousExecutionService:
    """
    ينسق تقييم وتنفيذ القرارات الآلية مع الحجز والتدقيق وحالة التشغيل والتاريخ.
    """

    def __init__(self, *, repository: AutonomousRemediationRepositoryPort,
                 remediation_repository: RemediationRepositoryPort, remediation_service,
                 policy_service, history_service, candidate_service, authorization_service,
                 evaluator=None, automatic_remediation_allowed=False):
        """
        يربط مستودعات القرار والحجز والتفويض والتدقيق والسياسة والمنفذ وحالة التشغيل والتاريخ.
        """
        self._repository = repository
        self._remediation_repository = remediation_repository
        self._remediation_service = remediation_service
        self._policy_service = policy_service
        self._history_service = history_service
        self._candidate_service = candidate_service
        self._authorization_service = authorization_service
        self._evaluator = evaluator or AutonomousRemediationPolicyEvaluator()
        self._automatic_remediation_allowed = automatic_remediation_allowed
        self._evaluation_handler = AutonomousPolicyEvaluationHandler()
        self._attempt_handler = AutonomousAttemptHandler()
        self._runtime_recorder = AutonomousRuntimeRecorder()


    def evaluate(self, *, plan_id: str):
        """يقيّم الخطة عبر معالج السياسة المنفصل."""
        return self._evaluation_handler.evaluate(self, plan_id=plan_id)

    @staticmethod
    def _select_policy(matches):
        """يحافظ على واجهة اختيار السياسة السابقة."""
        return AutonomousPolicyEvaluationHandler.select_policy(matches)

    def attempt(
        self,
        *,
        plan_id: str,
        actor: str = "autonomous-policy",
        idempotency_key: str | None = None,
    ):
        """ينفذ المحاولة عبر معالج التنفيذ المنفصل."""
        return self._attempt_handler.attempt(
            self,
            plan_id=plan_id,
            actor=actor,
            idempotency_key=idempotency_key,
        )

    def _replay_existing_reservation(self, *, existing, plan, action, idempotency_key: str, decision=None):
        """
        يعيد عرض نتيجة حجز سابق عند اكتشاف محاولة تنفيذ مكررة.
        """
        if not self._reservation_matches(
            reservation=existing, plan=plan, action=action, idempotency_key=idempotency_key,
        ):
            return {
                "outcome": "deny",
                "error": "idempotency_reservation_binding_mismatch",
                "reservation": self._reservation_view(existing),
            }
        if existing.status in {"reserved", "in_progress"}:
            return {
                "outcome": "in_progress",
                "idempotent": True,
                "reservation": self._reservation_view(existing),
            }
        if existing.status != "completed":
            return {
                "outcome": "deny",
                "error": "idempotency_reservation_not_replayable",
                "reservation": self._reservation_view(existing),
            }
        if not existing.execution_id:
            return {
                "outcome": "deny",
                "error": "completed_reservation_missing_execution",
                "reservation": self._reservation_view(existing),
            }
        execution = self._remediation_repository.get_execution(
            execution_id=existing.execution_id,
        )
        if execution is None or not self._execution_matches(
            execution=execution, reservation=existing, plan=plan, action=action,
        ):
            return {
                "outcome": "deny",
                "error": "completed_reservation_execution_binding_mismatch",
                "reservation": self._reservation_view(existing),
            }
        response = {
            "outcome": decision.outcome.value if decision is not None else "auto_execute",
            "idempotent": True,
            "reservation": self._reservation_view(existing),
            "execution": execution,
            "execution_id": execution.execution_id,
        }
        if decision is not None:
            response["decision"] = decision
        return response

    @staticmethod
    def _reservation_lease_stale(reservation, *, now) -> bool:
        """
        يتحقق من انتهاء مدة حجز تنفيذ سابق وإمكانية استعادته.
        """
        if reservation.status not in {"reserved", "in_progress"}:
            return False
        expires_at = getattr(reservation, "expires_at", None)
        if expires_at is None:
            return False
        if expires_at.tzinfo is None and now.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=now.tzinfo)
        return expires_at <= now

    @staticmethod
    def _reservation_matches(*, reservation, plan, action, idempotency_key: str) -> bool:
        """
        يتحقق من أن الحجز يخص الخطة والسيرفر والتشخيص والقرار الحاليين.
        """
        return (
            reservation.idempotency_key == idempotency_key
            and reservation.plan_id == plan.plan_id
            and reservation.plan_fingerprint == plan.plan_fingerprint
            and reservation.server_id == plan.server_id
            and reservation.action_type == action.action_type
            and reservation.target == action.target
        )

    @staticmethod
    def _execution_matches(*, execution, reservation, plan, action) -> bool:
        """
        يتحقق من ارتباط سجل التنفيذ بنفس هوية الخطة والقرار والحجز.
        """
        return (
            execution.execution_id == reservation.execution_id
            and execution.idempotency_key == reservation.idempotency_key
            and execution.plan_id == plan.plan_id
            and execution.server_id == plan.server_id
            and execution.action_id == (action.action_id or action.action_type)
        )

    def candidates(self):
        """
        يعرض مرشحي المعالجة الآلية المتاحين لسياق محدد.
        """
        return self._candidate_service.list_candidates()

    def list_decisions(self, *, plan_id: str | None = None, limit: int = 100):
        """
        يعيد قرارات التقييم والتنفيذ مع مرشحات السيرفر أو التشخيص.
        """
        return self._repository.list_decisions(plan_id=plan_id, limit=min(max(limit, 1), 500))

    def get_decision(self, decision_id: str):
        """
        يجلب قرارًا آليًا واحدًا ويرفع خطأ عند عدم وجوده.
        """
        return self._repository.get_decision(decision_id)

    def list_reservations(self, *, policy_id: str | None = None, plan_id: str | None = None, limit: int = 100):
        """
        يعرض حجوزات التنفيذ الآلي لتتبع التكرار والمهل.
        """
        return self._repository.list_reservations(policy_id=policy_id, plan_id=plan_id, limit=min(max(limit, 1), 500))

    def list_authorizations(self, *, limit: int = 100):
        """
        يعرض التفويضات الآلية حسب سياق الخطة أو السيرفر.
        """
        return self._repository.list_authorizations(limit=min(max(limit, 1), 500))

    def list_policy_audit_events(self, *, policy_id: str | None = None, limit: int = 100):
        """
        يعرض أحداث تدقيق السياسات المرتبطة بالتنفيذ الآلي.
        """
        return self._repository.list_all_policy_audit_events(
            policy_id=policy_id, limit=min(max(limit, 1), 500)
        )

    def runtime_state(self, policy_id: str):
        """
        يعيد حالة التشغيل الحالية المرتبطة بتنفيذ آلي أو خطة.
        """
        return self._repository.get_runtime_state(policy_id)

    def history(self, *, issue_fingerprint: str, action_type: str, target: str):
        """
        يعيد لقطة تاريخية لعمليات المعالجة الآلية.
        """
        return self._history_service.snapshot(issue_fingerprint=issue_fingerprint, action_type=action_type, target=target)

    def _audit(self, plan_id: str, event_type: str, payload: dict) -> None:
        """
        يسجل حدث تدقيق لقرار أو تنفيذ آلي مع تفاصيله.
        """
        try:
            self._remediation_service.audit_autonomous(plan_id=plan_id, event_type=event_type, payload=payload)
        except (OperationalError, ValueError):
            return

    @staticmethod
    def _reservation_view(reservation) -> dict:
        """
        يحوّل سجل الحجز الداخلي إلى عرض عقدي آمن.
        """
        return {
            "reservation_id": reservation.reservation_id,
            "idempotency_key": reservation.idempotency_key,
            "status": reservation.status,
            "policy_id": reservation.policy_id,
            "plan_id": reservation.plan_id,
            "plan_fingerprint": reservation.plan_fingerprint,
            "server_id": reservation.server_id,
            "action_type": reservation.action_type,
            "target": reservation.target,
            "authorization_id": reservation.authorization_id,
            "execution_id": reservation.execution_id,
        }

    def _record_runtime(
        self,
        policy,
        decision,
        success: bool,
        execution_id: str | None,
        *,
        failure_key: str | None = None,
    ):
        """يحافظ على واجهة تسجيل حالة التشغيل السابقة."""
        return self._runtime_recorder.record(
            self,
            policy,
            decision,
            success,
            execution_id,
            failure_key=failure_key,
        )

    @staticmethod
    def _single_action(plan):
        """
        ينفذ فعلًا آليًا واحدًا مع حدود السياسة والتحقق المطلوبة.
        """
        actions = [RemediationAction.from_dict(item) for item in (plan.proposed_actions or [])]
        if len(actions) != 1:
            raise ValueError("Phase 7 requires exactly one registered action.")
        return actions[0]

    @staticmethod
    def _history_dict(history):
        """
        يحوّل سجلًا تاريخيًا داخليًا إلى قاموس قابل للعرض والتسجيل.
        """
        return {"issue_fingerprint": history.issue_fingerprint, "action_type": history.action_type, "target": history.target,
                "supervised_execution_count": history.supervised_execution_count, "verified_success_count": history.verified_success_count,
                "failed_execution_count": history.failed_execution_count, "rollback_failure_count": history.rollback_failure_count,
                "success_rate": history.success_rate, "failure_rate": history.failure_rate}
