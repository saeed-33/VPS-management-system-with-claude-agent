"""
خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع.
"""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import sessionmaker

from app.core.contracts.remediation.approval_status import ApprovalStatus
from app.core.contracts.remediation.create_remediation_plan_dto import CreateRemediationPlanDTO
from app.core.contracts.remediation.create_sandbox_result_dto import CreateSandboxResultDTO
from app.core.contracts.remediation.remediation_plan_status import RemediationPlanStatus
from app.core.contracts.remediation.remediation_risk import RemediationRisk
from app.core.contracts.remediation.rollback_status import RollbackStatus
from app.core.contracts.remediation.helpers import remediation_fingerprint
from app.core.utils.datetime import utc_now
from app.infrastructure.database.models.remediation.approval import RemediationApprovalModel
from app.infrastructure.database.models.remediation.audit_event import RemediationAuditEventModel
from app.infrastructure.database.models.remediation.execution import RemediationExecutionModel
from app.infrastructure.database.models.remediation.evidence import RemediationEvidenceModel
from app.infrastructure.database.models.remediation.plan import RemediationPlanModel
from app.infrastructure.database.models.remediation.rollback import RemediationRollbackModel
from app.infrastructure.database.models.remediation.sandbox_result import RemediationSandboxResultModel
from app.infrastructure.database.models.remediation.verification import RemediationVerificationModel
from app.infrastructure.database.models.remediation.sandbox_validation import SandboxValidationModel
from app.infrastructure.database.models.server.server import ServerModel
from app.infrastructure.database.session import SessionLocal


class _RemediationRepositoryMixin3:
    """ينظم مجموعة من عمليات المستودع."""

    def sandbox_evidence_belongs(self, *, validation) -> bool:
        """
        يتحقق من أن أدلة before وafter تخص اختبار sandbox المكتمل للخطة نفسها.

        يمنع هذا الفحص استخدام دليل اختبار من خطة أخرى لإصدار موافقة أو تنفيذ.
        """
        if validation is None:
            return False
        expected = set(validation.before_evidence_ids or ()) | set(validation.after_evidence_ids or ())
        if not expected:
            return False
        with self._session_factory() as session:
            rows = list(session.scalars(select(RemediationEvidenceModel).where(
                RemediationEvidenceModel.plan_id == validation.plan_id,
                RemediationEvidenceModel.execution_id == validation.validation_id,
                RemediationEvidenceModel.evidence_id.in_(expected),
            )).all())
            return {row.evidence_id for row in rows} == expected

    def expire_approval(self, approval_id: str) -> RemediationApprovalModel:
        """
        يعالج حالة معلقة أو منتهية في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع حتى لا تبقى الحالة مضللة بعد الانقطاع.
        """
        with self._session_factory() as session:
            approval = session.scalar(select(RemediationApprovalModel).where(RemediationApprovalModel.approval_id == approval_id))
            if approval is None:
                raise ValueError(f"Approval not found: {approval_id}")
            if approval.status == ApprovalStatus.APPROVED.value:
                raise ValueError("Approved remediation cannot be expired.")
            approval.status = ApprovalStatus.EXPIRED.value
            approval.decided_at = utc_now()
            plan = session.scalar(select(RemediationPlanModel).where(RemediationPlanModel.plan_id == approval.plan_id))
            if plan is not None:
                plan.approval_status = ApprovalStatus.EXPIRED.value
                plan.status = RemediationPlanStatus.BLOCKED.value
                session.add(plan)
            session.add(approval)
            session.commit()
            session.refresh(approval)
            return approval

    def create_execution(self, **data) -> RemediationExecutionModel:
        """
        ينشئ أو يحدث سجلًا في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = RemediationExecutionModel(**data)
        with self._session_factory() as session:
            existing = session.scalar(select(RemediationExecutionModel).where(RemediationExecutionModel.idempotency_key == model.idempotency_key))
            if existing is not None:
                return existing
            try:
                session.add(model)
                session.commit()
            except IntegrityError:
                session.rollback()
                existing = session.scalar(select(RemediationExecutionModel).where(RemediationExecutionModel.idempotency_key == model.idempotency_key))
                if existing is None:
                    raise
                return existing
            session.refresh(model)
            return model

    def get_execution(self, execution_id: str | None = None, *, idempotency_key: str | None = None) -> RemediationExecutionModel | None:
        """
        يسترجع سجلًا من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            if execution_id:
                return session.scalar(select(RemediationExecutionModel).where(RemediationExecutionModel.execution_id == execution_id))
            if idempotency_key:
                return session.scalar(select(RemediationExecutionModel).where(RemediationExecutionModel.idempotency_key == idempotency_key))
            raise ValueError("execution_id or idempotency_key is required.")

    def create_evidence(self, **data) -> RemediationEvidenceModel:
        """
        ينشئ أو يحدث سجلًا في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = RemediationEvidenceModel(**data)
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def get_evidence(self, evidence_id: str) -> RemediationEvidenceModel | None:
        """
        يسترجع سجلًا من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.scalar(
                select(RemediationEvidenceModel).where(
                    RemediationEvidenceModel.evidence_id == evidence_id
                )
            )

    def list_evidence(self, *, plan_id: str, execution_id: str | None = None) -> list[RemediationEvidenceModel]:
        """
        يعرض قائمة مرتبة من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = select(RemediationEvidenceModel).where(
                RemediationEvidenceModel.plan_id == plan_id
            ).order_by(RemediationEvidenceModel.created_at.asc(), RemediationEvidenceModel.id.asc())
            if execution_id is not None:
                statement = statement.where(RemediationEvidenceModel.execution_id == execution_id)
            return list(session.scalars(statement).all())

    def update_execution(self, execution_id: str, **updates) -> RemediationExecutionModel:
        """
        يحدّث انتقالًا أو إعدادًا في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.scalar(select(RemediationExecutionModel).where(RemediationExecutionModel.execution_id == execution_id))
            if model is None:
                raise ValueError(f"Execution not found: {execution_id}")
            for name, value in updates.items():
                if hasattr(model, name):
                    setattr(model, name, value)
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def mark_interrupted_executions(self) -> int:
        """
        ينقل سجلًا من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع إلى حالة تشغيلية جديدة مع حفظ سبب الانتقال.
        """
        with self._session_factory() as session:
            models = list(session.scalars(
                select(RemediationExecutionModel).where(
                    RemediationExecutionModel.status.in_([
                        "claimed", "running",
                    ])
                )
            ).all())
            for execution in models:
                execution.status = "blocked"
                execution.error = "execution_interrupted_requires_operator_review"
                execution.completed_at = utc_now()
                plan = session.scalar(select(RemediationPlanModel).where(RemediationPlanModel.plan_id == execution.plan_id))
                if plan is not None:
                    plan.status = RemediationPlanStatus.ROLLBACK_REQUIRED.value
                    plan.execution_status = "blocked"
                    plan.rollback_status = RollbackStatus.REQUIRED.value
                    session.add(plan)
                session.add(execution)
            session.commit()
            return len(models)

    def create_verification(self, **data) -> RemediationVerificationModel:
        """
        ينشئ أو يحدث سجلًا في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = RemediationVerificationModel(**data)
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def create_rollback(self, **data) -> RemediationRollbackModel:
        """
        ينشئ أو يحدث سجلًا في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = RemediationRollbackModel(**data)
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def get_rollback(self, rollback_id: str) -> RemediationRollbackModel | None:
        """
        يسترجع سجلًا من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.scalar(
                select(RemediationRollbackModel).where(
                    RemediationRollbackModel.rollback_id == rollback_id
                )
            )

    def append_audit_event(self, *, plan_id: str, event_type: str, actor: str | None = None,
                           server_id: int | None = None, runtime_session_id: str | None = None,
                           agent_job_id: str | None = None, payload: dict | None = None) -> RemediationAuditEventModel:
        """
        يسجل حدثًا أو نتيجة جديدة في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع مع إبقاء أثرها قابلًا للمراجعة.
        """
        model = RemediationAuditEventModel(
            event_id=str(uuid4()), plan_id=plan_id, event_type=event_type, actor=actor,
            server_id=server_id, runtime_session_id=runtime_session_id, agent_job_id=agent_job_id,
            payload=dict(payload or {}),
        )
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def list_audit_events(self, plan_id: str) -> list[RemediationAuditEventModel]:
        """
        يعرض قائمة مرتبة من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            return list(session.scalars(
                select(RemediationAuditEventModel)
                .where(RemediationAuditEventModel.plan_id == plan_id)
                .order_by(RemediationAuditEventModel.created_at.asc(), RemediationAuditEventModel.id.asc())
            ).all())

    def list_all_audit_events(
        self, *, plan_id: str | None = None, event_type: str | None = None, limit: int = 100
    ) -> list[RemediationAuditEventModel]:
        """
        يعرض قائمة مرتبة من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = (
                select(RemediationAuditEventModel)
                .order_by(RemediationAuditEventModel.created_at.desc())
                .limit(limit)
            )
            if plan_id:
                statement = statement.where(RemediationAuditEventModel.plan_id == plan_id)
            if event_type:
                statement = statement.where(RemediationAuditEventModel.event_type == event_type)
            return list(session.scalars(statement).all())
