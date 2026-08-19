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


class RemediationRollbackModel(Base):
    """
    سجل محاولة إعادة السيرفر إلى الحالة السابقة بعد فشل التحقق.
    """
    __tablename__ = "remediation_rollbacks"
    id: Mapped[int] = mapped_column(primary_key=True)
    rollback_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    execution_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    before_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    after_evidence_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

