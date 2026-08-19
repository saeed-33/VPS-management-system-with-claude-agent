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


class _RemediationRepositoryMixin2:
    """ينظم مجموعة من عمليات المستودع."""

    @staticmethod
    def _sandbox_pass_invalid_reason(*, plan, data: dict, session) -> str | None:
        """
        ينفذ تحققًا داخليًا لازمًا لحفظ أو قراءة خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع.
        """
        if data.get("plan_fingerprint") != plan.plan_fingerprint:
            return "plan_fingerprint_changed"
        if data.get("server_id") != plan.server_id:
            return "sandbox_server_mismatch"
        server = session.scalar(select(ServerModel).where(ServerModel.id == data["server_id"]))
        if server is None or server.name != data.get("server_name"):
            return "sandbox_server_name_mismatch"
        if data.get("verification_status") != "verified":
            return "sandbox_verification_not_verified"

        actions = plan.proposed_actions or []
        if len(actions) != 1:
            return "exactly_one_registered_action_required"
        action = actions[0]
        action_type = str(action.get("action_type") or action.get("type") or action.get("tool") or "")
        target = str(action.get("target") or action.get("service") or "")
        if data.get("action_type") != action_type:
            return "sandbox_action_mismatch"
        if data.get("service") != target:
            return "sandbox_target_mismatch"
        if data.get("action_parameters") != (action.get("parameters") or {}):
            return "sandbox_action_parameters_mismatch"
        if not data.get("before_evidence_ids") or not data.get("after_evidence_ids"):
            return "sandbox_evidence_incomplete"

        metadata = data.get("validation_metadata") or {}
        if (
            not metadata.get("runtime")
            or metadata.get("runtime_available") is not True
            or not isinstance(metadata.get("runtime_evidence"), dict)
        ):
            return "native_sandbox_runtime_evidence_missing"

        before_ids = list(data["before_evidence_ids"])
        after_ids = list(data["after_evidence_ids"])
        expected_ids = set(before_ids) | set(after_ids)
        if len(expected_ids) != len(before_ids) + len(after_ids):
            return "sandbox_evidence_ids_overlap"
        rows = list(session.scalars(
            select(RemediationEvidenceModel).where(
                RemediationEvidenceModel.plan_id == plan.plan_id,
                RemediationEvidenceModel.execution_id == data["validation_id"],
                RemediationEvidenceModel.evidence_id.in_(expected_ids),
            )
        ).all())
        rows_by_id = {row.evidence_id: row for row in rows}
        if set(rows_by_id) != expected_ids:
            return "sandbox_evidence_ownership_invalid"
        if any(
            row.server_id != data["server_id"] or row.service != data["service"]
            for row in rows
        ):
            return "sandbox_evidence_binding_mismatch"
        if any(not row.observed_state for row in rows):
            return "sandbox_evidence_state_missing"
        if any(rows_by_id[item].phase != "sandbox_before" for item in before_ids):
            return "sandbox_before_evidence_invalid"
        if any(rows_by_id[item].phase != "sandbox_after" for item in after_ids):
            return "sandbox_after_evidence_invalid"
        if any(rows_by_id[item].observed_state not in {"active", "inactive"} for item in before_ids):
            return "sandbox_before_evidence_state_invalid"
        if any(rows_by_id[item].observed_state != data.get("expected_state") for item in after_ids):
            return "sandbox_after_evidence_state_invalid"
        return None

    def get_sandbox_validation(self, validation_id: str) -> SandboxValidationModel | None:
        """
        يسترجع سجلًا من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        try:
            with self._session_factory() as session:
                return session.scalar(select(SandboxValidationModel).where(
                    SandboxValidationModel.validation_id == validation_id
                ))
        except OperationalError:
            return None

    def get_latest_sandbox_validation(self, plan_id: str) -> SandboxValidationModel | None:
        """
        يسترجع سجلًا من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        try:
            with self._session_factory() as session:
                return session.scalar(
                    select(SandboxValidationModel)
                    .where(SandboxValidationModel.plan_id == plan_id)
                    .order_by(SandboxValidationModel.created_at.desc(), SandboxValidationModel.id.desc())
                )
        except OperationalError:
            return None

    def list_sandbox_validations(self, plan_id: str) -> list[SandboxValidationModel]:
        """
        يعرض قائمة مرتبة من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            return list(session.scalars(
                select(SandboxValidationModel)
                .where(SandboxValidationModel.plan_id == plan_id)
                .order_by(SandboxValidationModel.created_at.asc(), SandboxValidationModel.id.asc())
            ).all())

    def update_sandbox_validation(self, validation_id: str, **updates) -> SandboxValidationModel:
        """
        يحدّث انتقالًا أو إعدادًا في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.scalar(select(SandboxValidationModel).where(
                SandboxValidationModel.validation_id == validation_id
            ))
            if model is None:
                raise ValueError(f"Sandbox validation not found: {validation_id}")
            for name, value in updates.items():
                if hasattr(model, name):
                    setattr(model, name, value)
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def update_plan_status(self, plan_id: str, status: str, *, approved_by: str | None = None,
                           denial_reason: str | None = None, approval_requested: bool = False,
                           **updates) -> RemediationPlanModel:
        """
        يحدّث انتقالًا أو إعدادًا في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            plan = session.scalar(select(RemediationPlanModel).where(RemediationPlanModel.plan_id == plan_id))
            if plan is None:
                raise ValueError(f"Remediation plan not found: {plan_id}")
            plan.status = status
            if approval_requested:
                plan.approval_requested_at = utc_now()
            if approved_by is not None:
                plan.approved_by = approved_by
                plan.approved_at = utc_now()
            if denial_reason is not None:
                plan.denial_reason = denial_reason
            for name, value in updates.items():
                if hasattr(plan, name):
                    setattr(plan, name, value)
            session.add(plan)
            session.commit()
            session.refresh(plan)
            return plan

    def create_approval(self, *, plan_id: str, plan_fingerprint: str, expires_at: datetime | None = None,
                        scope: dict | None = None) -> RemediationApprovalModel:
        """
        ينشئ أو يحدث سجلًا في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = RemediationApprovalModel(
            approval_id=str(uuid4()),
            plan_id=plan_id,
            plan_fingerprint=plan_fingerprint,
            status=ApprovalStatus.PENDING.value,
            expires_at=expires_at,
            scope=dict(scope or {}),
        )
        with self._session_factory() as session:
            plan = session.scalar(select(RemediationPlanModel).where(RemediationPlanModel.plan_id == plan_id))
            if plan is None:
                raise ValueError(f"Remediation plan not found: {plan_id}")
            session.add(model)
            plan.status = RemediationPlanStatus.APPROVAL_REQUESTED.value
            plan.approval_status = ApprovalStatus.PENDING.value
            plan.approval_fingerprint = plan_fingerprint
            plan.approval_scope = dict(scope or {})
            plan.approval_expires_at = expires_at
            plan.approval_requested_at = utc_now()
            session.add(plan)
            session.commit()
            session.refresh(model)
            return model

    def get_approval(self, approval_id: str | None = None, *, plan_id: str | None = None) -> RemediationApprovalModel | None:
        """
        يسترجع سجلًا من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            if approval_id:
                return session.scalar(select(RemediationApprovalModel).where(RemediationApprovalModel.approval_id == approval_id))
            if plan_id:
                return session.scalar(
                    select(RemediationApprovalModel)
                    .where(RemediationApprovalModel.plan_id == plan_id)
                    .order_by(RemediationApprovalModel.created_at.desc(), RemediationApprovalModel.id.desc())
                )
            raise ValueError("approval_id or plan_id is required.")

    def get_latest_execution_for_plan(self, plan_id: str) -> RemediationExecutionModel | None:
        """
        يسترجع سجلًا من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.scalar(
                select(RemediationExecutionModel)
                .where(RemediationExecutionModel.plan_id == plan_id)
                .order_by(RemediationExecutionModel.created_at.desc(), RemediationExecutionModel.id.desc())
            )

    def decide_approval(self, approval_id: str, *, status: str, approver: str, comment: str | None = None,
                        scope: dict | None = None) -> RemediationApprovalModel:
        """
        يثبت قرارًا على سجل خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع مع الفاعل وسبب القرار ونطاقه.
        """
        if status not in {ApprovalStatus.APPROVED.value, ApprovalStatus.REJECTED.value, ApprovalStatus.CANCELLED.value}:
            raise ValueError("Invalid approval decision.")
        with self._session_factory() as session:
            approval = session.scalar(select(RemediationApprovalModel).where(RemediationApprovalModel.approval_id == approval_id))
            if approval is None:
                raise ValueError(f"Approval not found: {approval_id}")
            if approval.status != ApprovalStatus.PENDING.value:
                raise ValueError(f"Approval is already {approval.status}.")
            approval.status = status
            approval.approver = approver
            approval.comment = comment
            if scope is not None:
                approval.scope = dict(scope)
            approval.decided_at = utc_now()
            plan = session.scalar(select(RemediationPlanModel).where(RemediationPlanModel.plan_id == approval.plan_id))
            if plan is not None:
                plan.approval_status = status
                plan.approved_by = approver if status == ApprovalStatus.APPROVED.value else None
                plan.approved_at = utc_now() if status == ApprovalStatus.APPROVED.value else None
                plan.status = (
                    RemediationPlanStatus.APPROVED.value
                    if status == ApprovalStatus.APPROVED.value
                    else RemediationPlanStatus.REJECTED.value
                )
                session.add(plan)
            session.add(approval)
            session.commit()
            session.refresh(approval)
            return approval
