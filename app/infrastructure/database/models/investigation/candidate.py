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
from .investigation import InvestigationModel


class InvestigationSpecialistCandidateModel(Base):
    """
    مرشح متخصص محفوظ مع درجة المطابقة وأسبابها وحالة اختياره للتحقيق.
    """
    __tablename__ = "investigation_specialist_candidates"
    __table_args__ = (
        UniqueConstraint(
            "investigation_id",
            "specialist_slug",
            name="uq_investigation_candidate_slug",
        ),
        CheckConstraint("candidate_rank >= 1", name="ck_investigation_candidates_rank"),
        CheckConstraint(
            "selected_rank IS NULL OR selected_rank >= 1",
            name="ck_investigation_candidates_selected_rank",
        ),
        Index(
            "ix_investigation_candidates_investigation_rank",
            "investigation_id",
            "candidate_rank",
        ),
        Index(
            "ix_investigation_candidates_selected",
            "investigation_id",
            "is_selected",
            "selected_rank",
        ),
        Index("ix_investigation_candidates_specialist_slug", "specialist_slug"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(
        ForeignKey("investigations.id", ondelete="CASCADE"),
        nullable=False,
    )
    specialist_definition_id: Mapped[int | None] = mapped_column(
        ForeignKey("specialist_definitions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    specialist_slug: Mapped[str] = mapped_column(String(100), nullable=False)
    specialist_name: Mapped[str] = mapped_column(String(150), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    is_selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    selected_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    matched_domains: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    matched_trigger_hints: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    matched_issue_indexes: Mapped[list[int]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    investigation: Mapped[InvestigationModel] = relationship(back_populates="candidates")

