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


class _RemediationRepositoryMixin1:
    """ينظم مجموعة من عمليات المستودع."""

    def create_plan(self, data: CreateRemediationPlanDTO) -> RemediationPlanModel:
        """
        ينشئ أو يحدث سجلًا في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
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
        """
        يسترجع سجلًا من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.scalar(select(RemediationPlanModel).where(RemediationPlanModel.plan_id == plan_id))

    def get_latest_plan_for_investigation(
        self,
        investigation_id: str,
    ) -> RemediationPlanModel | None:
        """
        يعيد أحدث خطة مرتبطة بتحقيق لمنع إنشاء اقتراحات مكررة عند استئناف
        التحقيق أو إعادة إنهاء المتخصص نفسه.
        """
        with self._session_factory() as session:
            statement = (
                select(RemediationPlanModel)
                .where(RemediationPlanModel.investigation_id == investigation_id)
                .order_by(
                    RemediationPlanModel.created_at.desc(),
                    RemediationPlanModel.id.desc(),
                )
                .limit(1)
            )
            return session.scalar(statement)

    def create_no_solution_plan(self, *, plan_id: str, investigation_id: str, title: str,
                                problem_summary: str, diagnosis_claim_ids: list[str],
                                evidence_ids: list[str], server_id: int | None = None) -> RemediationPlanModel:
        """
        ينشئ أو يحدث سجلًا في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
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
        """
        يعرض قائمة مرتبة من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = select(RemediationPlanModel).order_by(RemediationPlanModel.created_at.desc()).limit(limit)
            if status:
                statement = statement.where(RemediationPlanModel.status == status)
            return list(session.scalars(statement).all())

    def create_sandbox_result(self, data: CreateSandboxResultDTO) -> RemediationSandboxResultModel:
        """
        ينشئ أو يحدث سجلًا في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
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
        """
        يسترجع سجلًا من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.scalar(select(RemediationSandboxResultModel).where(RemediationSandboxResultModel.result_id == result_id))

    def get_latest_sandbox_result_for_plan(self, plan_id: str) -> RemediationSandboxResultModel | None:
        """
        يسترجع سجلًا من خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.scalar(
                select(RemediationSandboxResultModel)
                .where(RemediationSandboxResultModel.plan_id == plan_id)
                .order_by(RemediationSandboxResultModel.created_at.desc(), RemediationSandboxResultModel.id.desc())
            )

    def create_sandbox_validation(self, **data) -> SandboxValidationModel:
        """
        ينشئ أو يحدث سجلًا في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = SandboxValidationModel(**data)
        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def finalize_sandbox_validation(self, **data) -> SandboxValidationModel:
        """
        يثبت النتيجة النهائية في خطط المعالجة ونتائج sandbox والموافقات والتنفيذ والأدلة والتحقق والتراجع قبل إعلان اكتمال المرحلة التالية.
        """
        with self._session_factory() as session:
            plan = session.scalar(
                select(RemediationPlanModel)
                .where(RemediationPlanModel.plan_id == data["plan_id"])
                .with_for_update()
            )
            if plan is None:
                raise ValueError(f"Remediation plan not found: {data['plan_id']}")

            status = data.get("status")
            if status == "passed":
                reason = self._sandbox_pass_invalid_reason(plan=plan, data=data, session=session)
                if reason is not None:
                    data = dict(data)
                    data["status"] = "stale" if reason == "plan_fingerprint_changed" else "failed"
                    data["failure_reason"] = reason
                elif plan.status in {
                    RemediationPlanStatus.PROPOSED.value,
                    RemediationPlanStatus.SANDBOX_FAILED.value,
                    RemediationPlanStatus.SANDBOX_PASSED.value,
                }:
                    plan.status = RemediationPlanStatus.SANDBOX_PASSED.value
                    session.add(plan)

            model = SandboxValidationModel(**data)
            session.add(model)
            session.commit()
            session.refresh(model)
            return model
