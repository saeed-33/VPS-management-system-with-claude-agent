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


class RemediationSandboxResultModel(Base):
    """
    نتيجة اختبار أولي للخطة في بيئة معزولة مع أدلة الحالة قبل وبعد.
    """
    __tablename__ = "remediation_sandbox_results"
    __table_args__ = (
        Index(
            "ix_remediation_sandbox_plan_created",
            "plan_id",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    result_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )
    plan_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    before_evidence_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    after_evidence_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    logs: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    result_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

