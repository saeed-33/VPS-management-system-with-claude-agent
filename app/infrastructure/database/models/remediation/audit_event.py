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


class RemediationAuditEventModel(Base):
    """
    حدث تدقيق يغطي انتقالات خطة المعالجة والفاعل والجلسة والأثر.
    """
    __tablename__ = "remediation_audit_events"
    __table_args__ = (
        Index("ix_remediation_audit_plan_created", "plan_id", "created_at"),
        Index("ix_remediation_audit_event_type", "event_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    actor: Mapped[str | None] = mapped_column(String(120), nullable=True)
    server_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    runtime_session_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    agent_job_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

