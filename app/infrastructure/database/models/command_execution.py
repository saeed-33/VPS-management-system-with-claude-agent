"""
نموذج نتيجة فحص واحد نفذته دورة المراقبة على السيرفر.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlmodel import JSON

from app.infrastructure.database.base import Base


class CommandExecutionModel(Base):
    """
    نتيجة فحص محفوظة داخل تقرير، بما في ذلك المخرج والخطأ والمدة والبصمة.
    """
    __tablename__ = "command_executions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    fingerprint_strategy: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="full_output",
    )

    fingerprint_config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    report_id: Mapped[int] = mapped_column(
        ForeignKey(
            "monitoring_reports.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    command_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "monitor_commands.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    command_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    # نحفظ نسخة من نص الأمر حتى لا تتغير
    # التقارير القديمة إذا عدّل المستخدم الأمر.
    command_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    execution_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    exit_status: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    stdout: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    stderr: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    error_message: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    duration_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    report: Mapped["MonitoringReportModel"] = (
        relationship(
            back_populates="executions",
        )
    )
