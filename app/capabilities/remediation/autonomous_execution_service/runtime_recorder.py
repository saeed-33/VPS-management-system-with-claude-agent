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


class AutonomousRuntimeRecorder:
    """يسجل حالة التشغيل والعدادات بعد القرارات الآلية."""

    def record(
        self, service, policy, decision, success: bool, execution_id: str | None,
        *, failure_key: str | None = None,
    ):
        """
        يحفظ انتقال حالة التشغيل ونتيجته ضمن سجل التنفيذ.
        """
        if success:
            recorder = getattr(service._repository, "record_autonomous_success", None)
            if recorder is not None:
                try:
                    return recorder(policy_id=policy.policy_id, policy_version=getattr(decision, "policy_version", None))
                except OperationalError:
                    # قد تفتقد بعض السجلات القديمة جدول سياسة المعالجة؛ نحافظ
                    # على قراءة الحالة دون اعتبار ذلك إذنًا لتغيير السيرفر.
                    pass
            return service._repository.update_runtime_state(
                policy.policy_id, last_execution_at=utc_now(), consecutive_failures=0,
                triggering_execution_id=None, triggering_decision_id=None,
            )

        recorder = getattr(service._repository, "record_autonomous_failure", None)
        if recorder is None:
            current = service._repository.get_runtime_state(policy.policy_id)
            return service._repository.update_runtime_state(
                policy.policy_id, last_execution_at=utc_now(),
                consecutive_failures=int(current.consecutive_failures) + 1,
                suspended_at=utc_now() if getattr(policy, "auto_suspend_on_failure", False) else None,
                suspension_reason="execution_failure" if getattr(policy, "auto_suspend_on_failure", False) else None,
                triggering_execution_id=execution_id or failure_key,
                triggering_decision_id=getattr(decision, "decision_id", None),
            )

        try:
            runtime, counted, tripped, stale_policy = recorder(
                policy_id=policy.policy_id,
                policy_version=getattr(decision, "policy_version", None),
                failure_key=failure_key or execution_id or getattr(decision, "decision_id", None),
                decision_id=getattr(decision, "decision_id", None),
                execution_id=execution_id,
            )
        except OperationalError:
            current = service._repository.get_runtime_state(policy.policy_id)
            return service._repository.update_runtime_state(
                policy.policy_id, last_execution_at=utc_now(),
                consecutive_failures=int(current.consecutive_failures) + 1,
                triggering_execution_id=execution_id or failure_key,
                triggering_decision_id=getattr(decision, "decision_id", None),
            )
        if counted:
            service._audit(decision.plan_id, "autonomous_runtime_failure_recorded", {
                "policy_id": policy.policy_id,
                "policy_version": getattr(decision, "policy_version", None),
                "failure_key": failure_key or execution_id,
                "execution_id": execution_id,
                "consecutive_failures": runtime.consecutive_failures,
            })
        if tripped:
            service._audit(decision.plan_id, "autonomous_circuit_breaker_tripped", {
                "policy_id": policy.policy_id,
                "policy_version": getattr(decision, "policy_version", None),
                "consecutive_failures": runtime.consecutive_failures,
                "threshold": getattr(policy, "max_consecutive_failures", 1),
            })
            service._audit(decision.plan_id, "autonomous_policy_suspended", {
                "policy_id": policy.policy_id,
                "policy_version": getattr(decision, "policy_version", None),
                "reason": "consecutive_failure_threshold",
            })
        return runtime

    
