"""
نماذج دورة المعالجة من الخطة والاختبار والموافقة حتى التنفيذ والتحقق والتراجع.

تضم أيضًا سجلات قرار المعالجة الذاتية وحجوزها وحالتها وأحداث تدقيقها، حتى يكون
كل تغيير على السيرفر قابلًا للمراجعة وربطه بالتشخيص والخطة.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class AutonomousPolicyDecisionModel(Base):
    """
    قرار تقييم سياسة المعالجة الذاتية مع رموز أسبابه وارتباطاته.
    """
    __tablename__ = "autonomous_policy_decisions"
    __table_args__ = (
        Index("ix_autonomous_decisions_plan_created", "plan_id", "created_at"),
        Index("ix_autonomous_decisions_policy_created", "policy_id", "created_at"),
        Index("ix_autonomous_decisions_outcome", "outcome"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    decision_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    policy_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    policy_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    plan_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    issue_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    server_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target: Mapped[str] = mapped_column(String(128), nullable=False)
    outcome: Mapped[str] = mapped_column(String(40), nullable=False)
    reason_codes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    human_readable_reasons: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    history_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    evaluation_metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

