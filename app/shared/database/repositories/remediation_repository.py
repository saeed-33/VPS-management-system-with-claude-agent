from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.shared.database.models.remediation import (
    RemediationPlanModel,
    RemediationSandboxResultModel,
)
from app.shared.database.session import SessionLocal
from app.shared.dto.remediation import (
    CreateRemediationPlanDTO,
    CreateSandboxResultDTO,
    RemediationPlanStatus,
)
from app.shared.utils.datetime import utc_now


class RemediationRepository:
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        self._session_factory = session_factory

    def create_plan(
        self,
        data: CreateRemediationPlanDTO,
    ) -> RemediationPlanModel:
        model = RemediationPlanModel(
            plan_id=data.plan_id,
            investigation_id=data.investigation_id,
            title=data.title,
            problem_summary=data.problem_summary,
            proposed_actions=list(
                data.proposed_actions
            ),
            diagnosis_claim_ids=list(
                data.diagnosis_claim_ids
            ),
            evidence_ids=list(
                data.evidence_ids
            ),
            risk_level=data.risk_level,
            rollback_plan=data.rollback_plan,
            status=(
                RemediationPlanStatus.PROPOSED.value
            ),
            plan_metadata=dict(
                data.metadata
            ),
        )

        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    def get_plan(
        self,
        plan_id: str,
    ) -> RemediationPlanModel | None:
        with self._session_factory() as session:
            return session.scalar(
                select(RemediationPlanModel).where(
                    RemediationPlanModel.plan_id
                    == plan_id
                )
            )

    def create_sandbox_result(
        self,
        data: CreateSandboxResultDTO,
    ) -> RemediationSandboxResultModel:
        model = RemediationSandboxResultModel(
            result_id=data.result_id,
            plan_id=data.plan_id,
            status=data.status,
            before_evidence_ids=list(
                data.before_evidence_ids
            ),
            after_evidence_ids=list(
                data.after_evidence_ids
            ),
            logs=list(data.logs),
            result_metadata=dict(
                data.metadata
            ),
        )

        with self._session_factory() as session:
            session.add(model)
            plan = session.scalar(
                select(RemediationPlanModel).where(
                    RemediationPlanModel.plan_id
                    == data.plan_id
                )
            )
            if plan is None:
                raise ValueError(
                    "Remediation plan not found: "
                    f"{data.plan_id}"
                )
            plan.sandbox_result_id = data.result_id
            plan.status = (
                RemediationPlanStatus
                .SANDBOX_PASSED
                .value
                if data.status == "passed"
                else RemediationPlanStatus
                .SANDBOX_FAILED
                .value
            )
            session.add(plan)
            session.commit()
            session.refresh(model)
            return model

    def get_sandbox_result(
        self,
        result_id: str,
    ) -> RemediationSandboxResultModel | None:
        with self._session_factory() as session:
            return session.scalar(
                select(
                    RemediationSandboxResultModel
                ).where(
                    RemediationSandboxResultModel
                    .result_id
                    == result_id
                )
            )

    def get_latest_sandbox_result_for_plan(
        self,
        plan_id: str,
    ) -> RemediationSandboxResultModel | None:
        with self._session_factory() as session:
            return session.scalar(
                select(
                    RemediationSandboxResultModel
                )
                .where(
                    RemediationSandboxResultModel
                    .plan_id
                    == plan_id
                )
                .order_by(
                    RemediationSandboxResultModel
                    .created_at
                    .desc(),
                    RemediationSandboxResultModel.id.desc(),
                )
            )

    def update_plan_status(
        self,
        plan_id: str,
        status: str,
        *,
        approved_by: str | None = None,
        denial_reason: str | None = None,
        approval_requested: bool = False,
    ) -> RemediationPlanModel:
        with self._session_factory() as session:
            plan = session.scalar(
                select(RemediationPlanModel).where(
                    RemediationPlanModel.plan_id
                    == plan_id
                )
            )
            if plan is None:
                raise ValueError(
                    "Remediation plan not found: "
                    f"{plan_id}"
                )

            plan.status = status
            if approval_requested:
                plan.approval_requested_at = (
                    utc_now()
                )
            if approved_by is not None:
                plan.approved_by = approved_by
                plan.approved_at = utc_now()
            if denial_reason is not None:
                plan.denial_reason = denial_reason

            session.add(plan)
            session.commit()
            session.refresh(plan)
            return plan
