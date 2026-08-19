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


class _AutonomousRemediationRepositoryMixin2:
    """ينظم مجموعة من عمليات المستودع."""

    def record_autonomous_failure(
        self, *, policy_id: str, policy_version: int | None, failure_key: str,
        decision_id: str | None, execution_id: str | None = None, now=None,
    ):
        """
        يسجل حدثًا أو نتيجة جديدة في سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها مع إبقاء أثرها قابلًا للمراجعة.
        """
        if not failure_key:
            raise ValueError("failure_key must not be empty.")
        now = now or utc_now()
        with self._session_factory() as session:
            policy = session.scalar(
                select(AutonomousRemediationPolicyModel)
                .where(AutonomousRemediationPolicyModel.policy_id == policy_id)
                .with_for_update()
            )
            runtime = session.scalar(
                select(AutonomousPolicyRuntimeStateModel)
                .where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id)
                .with_for_update()
            )
            if runtime is None:
                runtime = AutonomousPolicyRuntimeStateModel(policy_id=policy_id)
                session.add(runtime)
                session.flush()
            if runtime.triggering_execution_id == failure_key and runtime.consecutive_failures > 0:
                session.commit()
                session.refresh(runtime)
                return runtime, False, False, False
            if policy is None or policy.version != policy_version:
                session.commit()
                session.refresh(runtime)
                return runtime, False, False, True
            if policy.status == AutonomousPolicyStatus.SUSPENDED.value:
                session.commit()
                session.refresh(runtime)
                return runtime, False, False, False

            # قد لا يفرض SQLite قفل الصف بالطريقة نفسها؛ لذلك يحرس التحديث
            # الشرطي عداد الفشل من الزيادة مرتين عند الإنهاء المتزامن.
            changed = session.execute(
                update(AutonomousPolicyRuntimeStateModel)
                .where(
                    AutonomousPolicyRuntimeStateModel.id == runtime.id,
                    or_(
                        AutonomousPolicyRuntimeStateModel.triggering_execution_id.is_(None),
                        AutonomousPolicyRuntimeStateModel.triggering_execution_id != failure_key,
                    ),
                )
                .values(
                    last_execution_at=now,
                    consecutive_failures=AutonomousPolicyRuntimeStateModel.consecutive_failures + 1,
                    triggering_execution_id=failure_key,
                    triggering_decision_id=decision_id,
                    updated_at=now,
                )
            )
            if changed.rowcount != 1:
                session.commit()
                current = session.scalar(
                    select(AutonomousPolicyRuntimeStateModel)
                    .where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id)
                )
                return current or runtime, False, False, False
            session.flush()
            runtime = session.scalar(
                select(AutonomousPolicyRuntimeStateModel)
                .where(AutonomousPolicyRuntimeStateModel.policy_id == policy_id)
            )
            threshold = max(1, int(policy.max_consecutive_failures or 1))
            trip = bool(
                policy.auto_suspend_on_failure
                and runtime.consecutive_failures >= threshold
                and policy.status == AutonomousPolicyStatus.ENABLED.value
            )
            if trip:
                policy.status = AutonomousPolicyStatus.SUSPENDED.value
                policy.updated_at = now
                runtime.suspended_at = now
                runtime.suspension_reason = "consecutive_failure_threshold"
                # نحفظ مفتاح الحراسة: معرف التنفيذ للفشل المعتاد أو معرف الحجز
                # عندما يقع الفشل قبل إنشاء سجل تنفيذ.
                runtime.triggering_execution_id = failure_key
            session.commit()
            session.refresh(runtime)
            session.refresh(policy)
            return runtime, True, trip, False

    def create_decision(self, decision: AutonomousPolicyDecision, *, history: dict, metadata: dict | None = None):
        """
        ينشئ أو يحدث سجلًا في سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = AutonomousPolicyDecisionModel(
            decision_id=decision.decision_id, policy_id=decision.policy_id,
            policy_version=decision.policy_version, plan_id=decision.plan_id or "",
            plan_fingerprint=decision.plan_fingerprint or "", issue_fingerprint=decision.issue_fingerprint or "",
            server_id=decision.server_id, action_type=decision.action_type or "", target=decision.target or "",
            outcome=decision.outcome.value, reason_codes=list(decision.reason_codes),
            human_readable_reasons=list(decision.human_readable_reasons), history_snapshot=history,
            evaluation_metadata=metadata or decision.metadata,
        )
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def list_decisions(self, *, plan_id: str | None = None, limit: int = 100):
        """
        يعرض قائمة مرتبة من سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = select(AutonomousPolicyDecisionModel).order_by(AutonomousPolicyDecisionModel.created_at.desc()).limit(limit)
            if plan_id:
                statement = statement.where(AutonomousPolicyDecisionModel.plan_id == plan_id)
            return list(session.scalars(statement).all())

    def get_decision(self, decision_id: str):
        """
        يسترجع سجلًا من سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.scalar(select(AutonomousPolicyDecisionModel).where(AutonomousPolicyDecisionModel.decision_id == decision_id))

    def create_authorization(self, authorization: AutonomousAuthorization):
        """
        ينشئ أو يحدث سجلًا في سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = AutonomousAuthorizationModel(
            authorization_id=authorization.authorization_id, token=authorization.token,
            status=authorization.status.value, policy_id=authorization.policy_id,
            policy_version=authorization.policy_version, decision_id=authorization.decision_id,
            plan_id=authorization.plan_id, plan_fingerprint=authorization.plan_fingerprint,
            server_id=authorization.server_id, action_type=authorization.action_type,
            target=authorization.target, sandbox_validation_id=authorization.sandbox_validation_id,
            issued_at=authorization.issued_at, expires_at=authorization.expires_at,
        )
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def consume_authorization(self, authorization_id: str, *, now: datetime):
        """
        يستهلك تفويض المعالجة الذاتية مرة واحدة بعد التحقق من صلاحيته الزمنية.

        يمنع الاستهلاك المتكرر أن تتحول موافقة واحدة إلى أكثر من تغيير فعلي.
        """
        with self._session_factory() as session:
            model = session.scalar(select(AutonomousAuthorizationModel).where(AutonomousAuthorizationModel.authorization_id == authorization_id).with_for_update())
            if model is None:
                raise ValueError("Autonomous authorization not found.")
            if model.status != AutonomousAuthorizationStatus.VALID.value:
                raise ValueError("Autonomous authorization is not valid.")
            expires_at = model.expires_at
            if expires_at.tzinfo is None and now.tzinfo is not None:
                expires_at = expires_at.replace(tzinfo=now.tzinfo)
            if expires_at <= now:
                model.status = AutonomousAuthorizationStatus.EXPIRED.value
                session.commit()
                raise ValueError("Autonomous authorization has expired.")
            model.status = AutonomousAuthorizationStatus.CONSUMED.value
            model.consumed_at = now
            session.commit()
            session.refresh(model)
            return model

    def get_authorization(self, authorization_id: str):
        """
        يسترجع سجلًا من سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.scalar(select(AutonomousAuthorizationModel).where(AutonomousAuthorizationModel.authorization_id == authorization_id))

    def list_authorizations(self, *, limit: int = 100):
        """
        يعرض قائمة مرتبة من سياسات المعالجة الذاتية وقراراتها وتفويضاتها وحجوزها وتاريخ نجاحها وفشلها مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = (
                select(AutonomousAuthorizationModel)
                .order_by(AutonomousAuthorizationModel.issued_at.desc())
                .limit(limit)
            )
            return list(session.scalars(statement).all())
