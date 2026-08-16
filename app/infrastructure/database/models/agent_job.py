"""
نموذج persistence يطابق entity أو projection مخزنة في PostgreSQL.

الموقع في المعمارية: Persistence model.
يُستدعى بواسطة: repositories وطبقة database.
يعتمد مباشرة على: app.infrastructure.database.base، app.core.utils.datetime.
الحد المعماري: لا يحتوي على orchestration أو اتصال خارجي.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
    يمثل AgentJobModel مسؤولية محددة داخل طبقة Persistence model.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه repositories وطبقة database
    ويعتمد على Base وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
