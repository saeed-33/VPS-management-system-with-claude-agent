"""دعم تحميل خطط المعالجة وتسجيل أحداث التدقيق."""
from __future__ import annotations

from sqlalchemy.exc import OperationalError


class _RemediationAuditMixin:
    """يوفر عمليات الوصول إلى الخطة وتسجيل أحداث دورة المعالجة."""

    def _require_plan(self, plan_id: str):
        if not plan_id.strip():
            raise ValueError("plan_id must not be empty.")
        plan = self._repository.get_plan(plan_id)
        if plan is None:
            raise ValueError(f"Remediation plan not found: {plan_id}")
        return plan

    def _audit(self, plan, event_type: str, payload: dict, actor: str | None = None,
               runtime_session_id: str | None = None, agent_job_id: str | None = None) -> None:
        try:
            self._repository.append_audit_event(
                plan_id=plan.plan_id,
                event_type=event_type,
                actor=actor,
                server_id=getattr(plan, "server_id", None),
                runtime_session_id=runtime_session_id,
                agent_job_id=agent_job_id,
                payload=payload,
            )
        except OperationalError:
            return

    def audit_autonomous(self, *, plan_id: str, event_type: str, payload: dict) -> None:
        self._audit(
            self._require_plan(plan_id),
            event_type,
            payload,
            actor="autonomous-policy",
        )
