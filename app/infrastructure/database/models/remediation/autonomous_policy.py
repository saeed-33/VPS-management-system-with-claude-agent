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


class AutonomousRemediationPolicyModel(Base):
    """
    سياسة محفوظة تحدد متى يسمح علاج معين بالتنفيذ الذاتي.
    """
    __tablename__ = "autonomous_remediation_policies"
    __table_args__ = (
        Index("ix_autonomous_policies_match", "issue_fingerprint", "allowed_action_type", "status"),
        Index("ix_autonomous_policies_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(4000), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    issue_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    allowed_action_type: Mapped[str] = mapped_column(String(80), nullable=False)
    allowed_target_pattern: Mapped[str] = mapped_column(String(128), nullable=False)
    maximum_risk: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    minimum_confidence: Mapped[float] = mapped_column(nullable=False, default=0.0)
    required_evidence: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    minimum_success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    maximum_failure_rate: Mapped[float] = mapped_column(nullable=False, default=0.0)
    maximum_rollback_failure_rate: Mapped[float] = mapped_column(nullable=False, default=0.0)
    allowed_server_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    allowed_server_tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    sandbox_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sandbox_max_age_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=3600)
    rollback_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_executions_per_hour: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_executions_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    max_consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    auto_suspend_on_failure: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

