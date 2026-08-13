from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.core.contracts.remediation import (
    ApprovalStatus,
    CreateRemediationPlanDTO,
    CreateSandboxResultDTO,
    RemediationPlanStatus,
    RemediationRisk,
    RollbackStatus,
    remediation_fingerprint,
)
from app.core.utils.datetime import utc_now
from app.infrastructure.database.models.remediation import (
    RemediationApprovalModel,
    RemediationAuditEventModel,
    RemediationExecutionModel,
    RemediationEvidenceModel,
    RemediationPlanModel,
    RemediationRollbackModel,
    RemediationSandboxResultModel,
    RemediationVerificationModel,
)
from app.infrastructure.database.session import SessionLocal


class RemediationRepository:
    def __init__(self, session_factory: sessionmaker = SessionLocal) -> None:
        self._session_factory = session_factory

    def create_plan(self, data: CreateRemediationPlanDTO) -> RemediationPlanModel:
        fingerprint = data.plan_fingerprint or remediation_fingerprint(
            plan_id=data.plan_id,
            version=data.plan_version,
            server_id=data.server_id,
            actions=list(data.proposed_actions),
            evidence_ids=list(data.evidence_ids),
        )
        model = RemediationPlanModel(
            plan_id=data.plan_id,
            investigation_id=data.investigation_id,
            server_id=data.server_id,
            title=data.title,
            problem_summary=data.problem_summary,
            proposed_actions=list(data.proposed_actions),
            diagnosis_claim_ids=list(data.diagnosis_claim_ids),
            evidence_ids=list(data.evidence_ids),
            risk_level=data.risk_level,
            plan_version=data.plan_version,
            plan_fingerprint=fingerprint,
            rollback_plan=data.rollback_plan,
            status=RemediationPlanStatus.PROPOSED.value,
            approval_status=None,
            execution_status=None,
            verification_status=None,
            rollback_status=None,
            plan_metadata=dict(data.metadata),
        )
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def get_plan(self, plan_id: str) -> RemediationPlanModel | None:
        with self._session_factory() as session:
            return session.scalar(select(RemediationPlanModel).where(RemediationPlanModel.plan_id == plan_id))

    def create_no_solution_plan(self, *, plan_id: str, investigation_id: str, title: str,
                                problem_summary: str, diagnosis_claim_ids: list[str],
                                evidence_ids: list[str], server_id: int | None = None) -> RemediationPlanModel:
        model = RemediationPlanModel(
            plan_id=plan_id,
            investigation_id=investigation_id,
            server_id=server_id,
            title=title,
            problem_summary=problem_summary,
            proposed_actions=[],
            diagnosis_claim_ids=list(diagnosis_claim_ids),
            evidence_ids=list(evidence_ids),
            risk_level=RemediationRisk.CRITICAL.value,
            plan_version=1,
            plan_fingerprint=remediation_fingerprint(
                plan_id=plan_id, version=1, server_id=server_id,
                actions=[], evidence_ids=evidence_ids,
            ),
            status=RemediationPlanStatus.NO_SOLUTION_FOUND.value,
            plan_metadata={"production_application_allowed": False},
        )
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def list_plans(self, *, limit: int = 100, status: str | None = None) -> list[RemediationPlanModel]:
        with self._session_factory() as session:
            statement = select(RemediationPlanModel).order_by(RemediationPlanModel.created_at.desc()).limit(limit)
            if status:
                statement = statement.where(RemediationPlanModel.status == status)
            return list(session.scalars(statement).all())

    def create_sandbox_result(self, data: CreateSandboxResultDTO) -> RemediationSandboxResultModel:
        model = RemediationSandboxResultModel(
            result_id=data.result_id,
            plan_id=data.plan_id,
            status=data.status,
            before_evidence_ids=list(data.before_evidence_ids),
            after_evidence_ids=list(data.after_evidence_ids),
            logs=list(data.logs),
            result_metadata=dict(data.metadata),
        )
        with self._session_factory() as session:
            session.add(model)
            plan = session.scalar(select(RemediationPlanModel).where(RemediationPlanModel.plan_id == data.plan_id))
            if plan is None:
                raise ValueError(f"Remediation plan not found: {data.plan_id}")
            plan.sandbox_result_id = data.result_id
            plan.status = (
                RemediationPlanStatus.SANDBOX_PASSED.value
                if data.status == "passed"
                else RemediationPlanStatus.SANDBOX_FAILED.value
            )
            session.add(plan)
            session.commit()
            session.refresh(model)
            return model

    def get_sandbox_result(self, result_id: str) -> RemediationSandboxResultModel | None:
        with self._session_factory() as session:
            return session.scalar(select(RemediationSandboxResultModel).where(RemediationSandboxResultModel.result_id == result_id))

    def get_latest_sandbox_result_for_plan(self, plan_id: str) -> RemediationSandboxResultModel | None:
        with self._session_factory() as session:
            return session.scalar(
                select(RemediationSandboxResultModel)
                .where(RemediationSandboxResultModel.plan_id == plan_id)
                .order_by(RemediationSandboxResultModel.created_at.desc(), RemediationSandboxResultModel.id.desc())
            )

    def update_plan_status(self, plan_id: str, status: str, *, approved_by: str | None = None,
                           denial_reason: str | None = None, approval_requested: bool = False,
                           **updates) -> RemediationPlanModel:
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
        with self._session_factory() as session:
            return session.scalar(
                select(RemediationExecutionModel)
                .where(RemediationExecutionModel.plan_id == plan_id)
                .order_by(RemediationExecutionModel.created_at.desc(), RemediationExecutionModel.id.desc())
            )

    def decide_approval(self, approval_id: str, *, status: str, approver: str, comment: str | None = None,
                        scope: dict | None = None) -> RemediationApprovalModel:
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

    def expire_approval(self, approval_id: str) -> RemediationApprovalModel:
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
        with self._session_factory() as session:
            if execution_id:
                return session.scalar(select(RemediationExecutionModel).where(RemediationExecutionModel.execution_id == execution_id))
            if idempotency_key:
                return session.scalar(select(RemediationExecutionModel).where(RemediationExecutionModel.idempotency_key == idempotency_key))
            raise ValueError("execution_id or idempotency_key is required.")

    def create_evidence(self, **data) -> RemediationEvidenceModel:
        model = RemediationEvidenceModel(**data)
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def get_evidence(self, evidence_id: str) -> RemediationEvidenceModel | None:
        with self._session_factory() as session:
            return session.scalar(
                select(RemediationEvidenceModel).where(
                    RemediationEvidenceModel.evidence_id == evidence_id
                )
            )

    def list_evidence(self, *, plan_id: str, execution_id: str | None = None) -> list[RemediationEvidenceModel]:
        with self._session_factory() as session:
            statement = select(RemediationEvidenceModel).where(
                RemediationEvidenceModel.plan_id == plan_id
            ).order_by(RemediationEvidenceModel.created_at.asc(), RemediationEvidenceModel.id.asc())
            if execution_id is not None:
                statement = statement.where(RemediationEvidenceModel.execution_id == execution_id)
            return list(session.scalars(statement).all())

    def update_execution(self, execution_id: str, **updates) -> RemediationExecutionModel:
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
        """Fail closed after process restart; never replay a write."""
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
        model = RemediationVerificationModel(**data)
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def create_rollback(self, **data) -> RemediationRollbackModel:
        model = RemediationRollbackModel(**data)
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def get_rollback(self, rollback_id: str) -> RemediationRollbackModel | None:
        with self._session_factory() as session:
            return session.scalar(
                select(RemediationRollbackModel).where(
                    RemediationRollbackModel.rollback_id == rollback_id
                )
            )

    def append_audit_event(self, *, plan_id: str, event_type: str, actor: str | None = None,
                           server_id: int | None = None, runtime_session_id: str | None = None,
                           agent_job_id: str | None = None, payload: dict | None = None) -> RemediationAuditEventModel:
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
        with self._session_factory() as session:
            return list(session.scalars(
                select(RemediationAuditEventModel)
                .where(RemediationAuditEventModel.plan_id == plan_id)
                .order_by(RemediationAuditEventModel.created_at.asc(), RemediationAuditEventModel.id.asc())
            ).all())
