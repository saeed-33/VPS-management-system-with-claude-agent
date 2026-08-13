from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    DateTime,
    Float,
    Boolean,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base
from app.shared.utils.datetime import utc_now


class AnalysisJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportAnalysisModel(Base):
    __tablename__ = "report_analyses"

    __table_args__ = (
        UniqueConstraint(
            "report_id",
            name="uq_report_analyses_report_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    report_id: Mapped[int] = mapped_column(
        ForeignKey(
            "monitoring_reports.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    server_id: Mapped[int] = mapped_column(
        ForeignKey(
            "servers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    provider_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=AnalysisJobStatus.PENDING.value,
        index=True,
    )

    health_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        index=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    issues: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    positive_findings: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    recommended_actions: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    analysis_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    duration_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    report_fingerprint: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    normalized_report: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    analysis_source: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="generated",
        index=True,
    )

    reused_from_analysis_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "report_analyses.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    retrieval_strategy: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    retrieval_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    llm_called: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    performance_metrics: Mapped[dict] = mapped_column(
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