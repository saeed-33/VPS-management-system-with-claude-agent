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


class AdminSessionModel(Base):
    """
    جلسة دخول إدارية مرتبطة بمستخدم ووقت انتهاء وآخر استخدام.
    """

    __tablename__ = "admin_sessions"
    __table_args__ = (
        Index("ix_admin_sessions_user_expires", "user_id", "expires_at"),
        Index("ix_admin_sessions_active_expires", "revoked_at", "expires_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_digest: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    remote_addr: Mapped[str | None] = mapped_column(String(128), nullable=True)

