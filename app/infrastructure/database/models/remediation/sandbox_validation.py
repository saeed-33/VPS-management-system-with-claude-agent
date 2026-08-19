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


class SandboxValidationModel(Base):
    """
    إثبات أن خطة محددة اجتازت اختبار sandbox المرتبط بهدفها وبصمتها.
    """
    __tablename__ = "sandbox_validations"
    __table_args__ = (
        Index("ix_sandbox_validations_plan_created", "plan_id", "created_at"),
        Index("ix_sandbox_validations_plan_fingerprint", "plan_id", "plan_fingerprint"),
        Index("ix_sandbox_validations_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    validation_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    plan_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id", ondelete="RESTRICT"), nullable=False, index=True)
    server_name: Mapped[str] = mapped_column(String(100), nullable=False)
    service: Mapped[str] = mapped_column(String(128), nullable=False)
    action_type: Mapped[str] = mapped_column(String(80), nullable=False)
    action_parameters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    expected_state: Mapped[str] = mapped_column(String(30), nullable=False)
    observed_state: Mapped[str | None] = mapped_column(String(30), nullable=True)
    before_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    after_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    verification_status: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    validation_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

