"""
سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import or_, select, update
from sqlalchemy.exc import IntegrityError

from app.core.contracts.autonomous_remediation.autonomous_authorization import AutonomousAuthorization
from app.core.contracts.autonomous_remediation.autonomous_authorization_status import AutonomousAuthorizationStatus
from app.core.contracts.autonomous_remediation.autonomous_history_snapshot import AutonomousHistorySnapshot
from app.core.contracts.autonomous_remediation.autonomous_policy_decision import AutonomousPolicyDecision
from app.core.contracts.autonomous_remediation.autonomous_policy_status import AutonomousPolicyStatus
from app.core.contracts.autonomous_remediation.autonomous_remediation_policy import AutonomousRemediationPolicy
from app.core.utils.datetime import utc_now
from app.infrastructure.database.models.remediation.autonomous_authorization import AutonomousAuthorizationModel
from app.infrastructure.database.models.remediation.autonomous_decision import AutonomousPolicyDecisionModel
from app.infrastructure.database.models.remediation.autonomous_reservation import AutonomousPolicyExecutionReservationModel
from app.infrastructure.database.models.remediation.autonomous_runtime import AutonomousPolicyRuntimeStateModel
from app.infrastructure.database.models.remediation.autonomous_audit_event import AutonomousPolicyAuditEventModel
from app.infrastructure.database.models.remediation.autonomous_policy import AutonomousRemediationPolicyModel
from app.infrastructure.database.models.remediation.evidence import RemediationEvidenceModel
from app.infrastructure.database.models.remediation.execution import RemediationExecutionModel
from app.infrastructure.database.models.remediation.plan import RemediationPlanModel
from app.infrastructure.database.models.remediation.rollback import RemediationRollbackModel
from app.infrastructure.database.models.remediation.verification import RemediationVerificationModel
from app.infrastructure.database.session import SessionLocal


class _RuntimeStateMixin:
    """ينظم مجموعة من عمليات المستودع."""

    def finalize_reservation(self, reservation_id: str, *, owner_token: str, status: str, execution_id: str | None = None):
        """
        يثبت النتيجة النهائية في سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها قبل إعلان اكتمال المرحلة التالية.
        """
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(AutonomousPolicyExecutionReservationModel.reservation_id == reservation_id).with_for_update())
            if model is None:
                raise ValueError("Autonomous reservation not found.")
            if model.owner_token != owner_token:
                raise ValueError("Autonomous reservation is owned by another worker.")
            if model.status not in {"reserved", "in_progress"}:
                raise ValueError("Autonomous reservation is not active.")
            model.status = status
            model.execution_id = execution_id
            model.completed_at = utc_now()
            session.commit()
            session.refresh(model)
            return model

    def update_reservation_authorization(self, reservation_id: str, *, owner_token: str, authorization_id: str):
        """
        يحدّث انتقالًا أو إعدادًا في سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousPolicyExecutionReservationModel).where(AutonomousPolicyExecutionReservationModel.reservation_id == reservation_id).with_for_update())
            if model is None:
                raise ValueError("Autonomous reservation not found.")
            if model.owner_token != owner_token:
                raise ValueError("Autonomous reservation is owned by another worker.")
            if model.status not in {"reserved", "in_progress"}:
                raise ValueError("Autonomous reservation is not active.")
            if model.authorization_id is not None and model.authorization_id != authorization_id:
                raise ValueError("Autonomous reservation already has an authorization.")
            model.authorization_id = authorization_id
            session.commit()
            session.refresh(model)
            return model

    def get_runtime_state(self, policy_id: str):
        """
        يسترجع سجلًا من سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousPolicyRuntimeStateModel).where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id))
            if model is None:
                model = AutonomousPolicyRuntimeStateModel(policy_id=policy_id)
                session.add(model)
                session.commit()
                session.refresh(model)
            return model

    def list_reservations(self, *, policy_id: str | None = None, plan_id: str | None = None, limit: int = 100):
        """
        يعرض قائمة مرتبة من سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = select(AutonomousPolicyExecutionReservationModel).order_by(AutonomousPolicyExecutionReservationModel.created_at.desc()).limit(limit)
            if policy_id:
                statement = statement.where(AutonomousPolicyExecutionReservationModel.policy_id == policy_id)
            if plan_id:
                statement = statement.where(AutonomousPolicyExecutionReservationModel.plan_id == plan_id)
            return list(session.scalars(statement).all())

    def get_reservation_by_idempotency_key(self, idempotency_key: str):
        """
        يسترجع سجلًا من سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.scalar(
                select(AutonomousPolicyExecutionReservationModel).where(
                    AutonomousPolicyExecutionReservationModel.idempotency_key == idempotency_key
                )
            )

    def update_runtime_state(self, policy_id: str, **updates):
        """
        يحدّث انتقالًا أو إعدادًا في سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousPolicyRuntimeStateModel).where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id).with_for_update())
            if model is None:
                model = AutonomousPolicyRuntimeStateModel(policy_id=policy_id)
                session.add(model)
                session.flush()
            for key, value in updates.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            model.updated_at = utc_now()
            session.commit()
            session.refresh(model)
            return model

    def append_policy_audit_event(self, *, policy_id: str, policy_version: int, event_type: str,
                                  actor: str = "admin", payload: dict | None = None):
        """
        يسجل حدثًا أو نتيجة جديدة في سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها مع إبقاء أثرها قابلًا للمراجعة.
        """
        model = AutonomousPolicyAuditEventModel(
            event_id=str(uuid4()), policy_id=policy_id, policy_version=policy_version,
            event_type=event_type, actor=actor, payload=dict(payload or {}),
        )
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def list_policy_audit_events(self, policy_id: str):
        """
        يعرض قائمة مرتبة من سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            return list(session.scalars(
                select(AutonomousPolicyAuditEventModel)
                .where(AutonomousPolicyAuditEventModel.policy_id == policy_id)
                .order_by(AutonomousPolicyAuditEventModel.created_at.asc(), AutonomousPolicyAuditEventModel.id.asc())
            ).all())

    def list_all_policy_audit_events(self, *, policy_id: str | None = None, limit: int = 100):
        """
        يعرض قائمة مرتبة من سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = (
                select(AutonomousPolicyAuditEventModel)
                .order_by(AutonomousPolicyAuditEventModel.created_at.desc())
                .limit(limit)
            )
            if policy_id:
                statement = statement.where(
                    AutonomousPolicyAuditEventModel.policy_id == policy_id
                )
            return list(session.scalars(statement).all())

    def history(self, *, issue_fingerprint: str, action_type: str, target: str) -> AutonomousHistorySnapshot:
        """
        يجمع تاريخ سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها وعداداته لتستخدمها سياسة السلامة في القرار.
        """
        with self._session_factory() as session:
            plans = list(session.scalars(select(RemediationPlanModel)).all())
            plan_ids = {
                plan.plan_id for plan in plans
                if (
                    isinstance((plan.plan_metadata or {}).get("issue_fingerprint"), str)
                    and (plan.plan_metadata or {}).get("issue_fingerprint").strip()
                    and (plan.plan_metadata or {}).get("issue_fingerprint") == issue_fingerprint
                )
            }
            executions = list(session.scalars(select(RemediationExecutionModel).where(RemediationExecutionModel.plan_id.in_(plan_ids))).all()) if plan_ids else []
            verified_ids = {item.execution_id for item in session.scalars(select(RemediationVerificationModel).where(RemediationVerificationModel.status == "verified", RemediationVerificationModel.execution_id.in_([e.execution_id for e in executions]))).all()} if executions else set()
            rollback_rows = list(session.scalars(select(RemediationRollbackModel).where(RemediationRollbackModel.execution_id.in_([e.execution_id for e in executions]))).all()) if executions else []
            eligible_plan_ids = {
                plan.plan_id for plan in plans
                if plan.plan_id in plan_ids and any(
                    str(action.get("action_type") or action.get("type") or action.get("tool") or "") == action_type
                    and str(action.get("target") or action.get("service") or "") == target
                    for action in (plan.proposed_actions or [])
                )
            }
            supervised = [item for item in executions if item.plan_id in eligible_plan_ids and not (item.execution_metadata or {}).get("autonomous")]
            successes = [item for item in supervised if item.status == "succeeded"]
            failures = [item for item in supervised if item.status == "failed"]
            rollback_required = [item for item in rollback_rows if item.status in {"succeeded", "failed"}]
            return AutonomousHistorySnapshot(
                issue_fingerprint=issue_fingerprint, action_type=action_type, target=target,
                supervised_execution_count=len(supervised), successful_execution_count=len(successes),
                failed_execution_count=len(failures), verified_success_count=len(set(item.execution_id for item in successes) & verified_ids),
                verification_failure_count=len(set(item.execution_id for item in successes) - verified_ids),
                rollback_required_count=len(rollback_required), rollback_success_count=sum(item.status == "succeeded" for item in rollback_required),
                rollback_failure_count=sum(item.status == "failed" for item in rollback_required),
                autonomous_execution_count=sum(bool((item.execution_metadata or {}).get("autonomous")) for item in executions),
                autonomous_success_count=sum(bool((item.execution_metadata or {}).get("autonomous")) and item.status == "succeeded" for item in executions),
                autonomous_failure_count=sum(bool((item.execution_metadata or {}).get("autonomous")) and item.status != "succeeded" for item in executions),
                last_success_at=max((item.completed_at for item in successes if item.completed_at), default=None),
                last_failure_at=max((item.completed_at for item in failures if item.completed_at), default=None),
            )

    def execution_counts(self, *, policy_id: str, now: datetime):
        """
        يجمع تاريخ سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها وعداداته لتستخدمها سياسة السلامة في القرار.
        """
        from datetime import timedelta
        with self._session_factory() as session:
            rows = list(session.scalars(select(AutonomousPolicyExecutionReservationModel).where(AutonomousPolicyExecutionReservationModel.policy_id == policy_id)).all())
            return {
                "hour": sum(item.created_at >= now - timedelta(hours=1) for item in rows),
                "day": sum(item.created_at >= now - timedelta(days=1) for item in rows),
                "last": max((item.created_at for item in rows), default=None),
            }

    @staticmethod
    def _aware(value, reference: datetime):
        """
        يوحد المنطقة الزمنية لقيمة تاريخية قبل مقارنة حالة سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها.
        """
        if value is None:
            return None
        if value.tzinfo is None and reference.tzinfo is not None:
            return value.replace(tzinfo=reference.tzinfo)
        return value

    @staticmethod
    def _policy_model(policy: AutonomousRemediationPolicy):
        """
        يحول عقد المجال إلى نموذج تخزين خاص بـسياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها.
        """
        return AutonomousRemediationPolicyModel(
            policy_id=policy.policy_id, name=policy.name, description=policy.description,
            status=policy.status.value, version=policy.version, issue_fingerprint=policy.issue_fingerprint,
            allowed_action_type=policy.allowed_action_type, allowed_target_pattern=policy.allowed_target_pattern,
            maximum_risk=policy.maximum_risk, minimum_confidence=policy.minimum_confidence,
            required_evidence=list(policy.required_evidence), minimum_success_count=policy.minimum_success_count,
            maximum_failure_rate=policy.maximum_failure_rate, maximum_rollback_failure_rate=policy.maximum_rollback_failure_rate,
            allowed_server_ids=list(policy.allowed_server_ids), allowed_server_tags=list(policy.allowed_server_tags),
            sandbox_required=policy.sandbox_required, sandbox_max_age_seconds=policy.sandbox_max_age_seconds,
            rollback_required=policy.rollback_required, cooldown_seconds=policy.cooldown_seconds,
            max_executions_per_hour=policy.max_executions_per_hour, max_executions_per_day=policy.max_executions_per_day,
            max_consecutive_failures=policy.max_consecutive_failures, auto_suspend_on_failure=policy.auto_suspend_on_failure,
            created_by=policy.created_by, updated_by=policy.updated_by,
        )
