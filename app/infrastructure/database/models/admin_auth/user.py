"""
نماذج مستخدمي الإدارة وجلساتهم وأحداث المصادقة.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.utils.datetime import utc_now
from app.infrastructure.database.base import Base


class AdminUserModel(Base):
    """
    سجل حساب إداري يمكنه طلب ومراجعة عمليات إدارة السيرفر.
    """

    __tablename__ = "admin_users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('viewer', 'operator', 'admin')",
            name="ck_admin_users_role",
        ),
        Index("ix_admin_users_active_role", "is_active", "role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

