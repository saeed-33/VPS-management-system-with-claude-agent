"""
نموذج ربط تحليل التقرير بالمصادر التي دعمت تفسيره.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class ReportAnalysisSourceModel(Base):
    """
    رابط يحفظ مصدر المعرفة أو التقرير الذي دخل في سياق تحليل معين.
    """
    __tablename__ = "report_analysis_sources"
    __table_args__ = (
        UniqueConstraint(
            "analysis_id",
            "source_type",
            "source_report_id",
            "source_analysis_id",
            name="uq_report_analysis_source_identity",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey(
            "report_analyses.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    source_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        index=True,
    )
    source_report_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "monitoring_reports.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    source_analysis_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "report_analyses.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    retrieval_strategy: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )
    similarity_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    rank: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )
    excerpt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    source_metadata: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    used_in_prompt: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
