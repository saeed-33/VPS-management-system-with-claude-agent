from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class RemediationPlanModel(Base):
    __tablename__ = "remediation_plans"
    __table_args__ = (
        Index(
            "ix_remediation_plans_investigation_created",
            "investigation_id",
            "created_at",
        ),
        Index(
            "ix_remediation_plans_status",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    plan_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )
    investigation_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    problem_summary: Mapped[str] = mapped_column(
        String(4000),
        nullable=False,
    )
    proposed_actions: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    diagnosis_claim_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    evidence_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    rollback_plan: Mapped[str | None] = mapped_column(
        String(4000),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )
    sandbox_result_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )
    approval_requested_at: Mapped[datetime | None] = (
        mapped_column(
            DateTime(timezone=True),
            nullable=True,
        )
    )
    approved_by: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    denial_reason: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
    plan_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )


class RemediationSandboxResultModel(Base):
    __tablename__ = "remediation_sandbox_results"
    __table_args__ = (
        Index(
            "ix_remediation_sandbox_plan_created",
            "plan_id",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    result_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )
    plan_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    before_evidence_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    after_evidence_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    logs: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    result_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
