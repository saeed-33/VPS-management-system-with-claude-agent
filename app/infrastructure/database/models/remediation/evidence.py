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


class RemediationEvidenceModel(Base):
    """
    دليل تشغيلي يجمعه مسار المعالجة قبل التغيير أو أثناءه أو بعده.
    """
    __tablename__ = "remediation_evidence"
    __table_args__ = (
        Index("ix_remediation_evidence_plan_created", "plan_id", "created_at"),
        Index("ix_remediation_evidence_execution_phase", "execution_id", "phase"),
        Index("ix_remediation_evidence_server_service", "server_id", "service"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    evidence_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    execution_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    server_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    service: Mapped[str] = mapped_column(String(128), nullable=False)
    phase: Mapped[str] = mapped_column(String(30), nullable=False)
    observed_state: Mapped[str] = mapped_column(String(30), nullable=False)
    evidence_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

