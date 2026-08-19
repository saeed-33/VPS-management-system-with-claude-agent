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


class RemediationExecutionModel(Base):
    """
    سجل تنفيذ فعلي لخطة المعالجة ونتيجته وأثره على السيرفر.
    """
    __tablename__ = "remediation_executions"
    __table_args__ = (
        Index("ix_remediation_executions_plan_created", "plan_id", "created_at"),
        Index("ix_remediation_executions_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    execution_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action_id: Mapped[str] = mapped_column(String(128), nullable=False)
    server_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    actor: Mapped[str | None] = mapped_column(String(120), nullable=True)
    runtime_session_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    agent_job_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    before_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    after_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    exit_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stdout: Mapped[str] = mapped_column(String(12000), nullable=False, default="")
    stderr: Mapped[str] = mapped_column(String(12000), nullable=False, default="")
    error: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)

