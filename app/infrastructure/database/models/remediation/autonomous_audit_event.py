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


class AutonomousPolicyAuditEventModel(Base):
    """
    حدث تدقيق لقرارات وحجوز وتنفيذات المعالجة الذاتية.
    """

    __tablename__ = "autonomous_policy_audit_events"
    __table_args__ = (
        Index("ix_autonomous_policy_audit_policy_created", "policy_id", "created_at"),
        Index("ix_autonomous_policy_audit_event_type", "event_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    policy_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    policy_version: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    actor: Mapped[str] = mapped_column(String(120), nullable=False, default="admin")
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

