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


class AdminAuthAuditEventModel(Base):
    """
    حدث تدقيق يثبت محاولات الدخول والخروج ونتائجها.
    """

    __tablename__ = "admin_auth_audit_events"
    __table_args__ = (
        Index("ix_admin_auth_audit_event_created", "event_type", "created_at"),
        Index("ix_admin_auth_audit_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    username: Mapped[str | None] = mapped_column(String(120), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    remote_addr: Mapped[str | None] = mapped_column(String(128), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(
        "metadata", JSON, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
