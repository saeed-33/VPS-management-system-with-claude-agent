"""
نماذج التحقيق ومرشحي المتخصصين الذين اختارهم التوجيه.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class InvestigationModel(Base):
    """
    سجل تحقيق يربط السيرفر بتقرير المراقبة والتحليل وقرار التوجيه وحالة التنفيذ.
    """
    __tablename__ = "investigations"
    __table_args__ = (
        CheckConstraint("candidate_limit >= 1", name="ck_investigations_candidate_limit"),
        CheckConstraint("selection_limit >= 1", name="ck_investigations_selection_limit"),
        CheckConstraint(
            "candidate_limit >= selection_limit",
            name="ck_investigations_candidate_selection_limits",
        ),
        CheckConstraint("max_specialists >= 1", name="ck_investigations_max_specialists"),
        CheckConstraint("max_rounds >= 1", name="ck_investigations_max_rounds"),
        CheckConstraint("max_actions >= 0", name="ck_investigations_max_actions"),
        Index("ix_investigations_server_created", "server_id", "created_at"),
        Index("ix_investigations_report", "report_id"),
        Index("ix_investigations_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    report_id: Mapped[int] = mapped_column(ForeignKey("monitoring_reports.id", ondelete="CASCADE"), nullable=False)
    analysis_id: Mapped[int | None] = mapped_column(
        ForeignKey("report_analyses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="created")
    should_investigate: Mapped[bool] = mapped_column(Boolean, nullable=False)
    routing_reasons: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    detected_domains: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    unmatched_issue_indexes: Mapped[list[int]] = mapped_column(JSON, nullable=False, default=list)
    registry_size: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    selection_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    max_specialists: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    max_rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    max_actions: Mapped[int] = mapped_column(Integer, nullable=False, default=12)
    routing_version: Mapped[str] = mapped_column(String(50), nullable=False, default="deterministic-v1")
    investigation_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    candidates: Mapped[list["InvestigationSpecialistCandidateModel"]] = relationship(
        back_populates="investigation",
        cascade="all, delete-orphan",
        order_by="InvestigationSpecialistCandidateModel.candidate_rank",
        lazy="selectin",
    )

