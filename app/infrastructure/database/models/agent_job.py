"""
نموذج سجل مهمة Claude أو العامل التشغيلي من الانتظار حتى النهاية.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class AgentJobModel(Base):
    """
    سجل مهمة Claude أو العامل التشغيلي مع سياقها وحالتها ونتيجتها وعدادات الجلسة.
    """
    __tablename__ = "agent_jobs"
    __table_args__ = (
        CheckConstraint(
            "turn_count >= 0",
            name="ck_agent_jobs_turn_count",
        ),
        CheckConstraint(
            "tool_call_count >= 0",
            name="ck_agent_jobs_tool_call_count",
        ),
        Index(
            "ix_agent_jobs_type_status_created",
            "job_type",
            "status",
            "created_at",
        ),
        Index(
            "ix_agent_jobs_server_created",
            "server_id",
            "created_at",
        ),
        Index(
            "ix_agent_jobs_status",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    job_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )
    job_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    server_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    claude_session_id: Mapped[str | None] = (
        mapped_column(
            String(120),
            nullable=True,
            index=True,
        )
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    completed_at: Mapped[datetime | None] = (
        mapped_column(
            DateTime(timezone=True),
            nullable=True,
        )
    )
    error_code: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )
    error_message: Mapped[str | None] = (
        mapped_column(
            String(2000),
            nullable=True,
        )
    )
    turn_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    tool_call_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    usage_metadata: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    job_metadata: Mapped[dict] = mapped_column(
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
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
