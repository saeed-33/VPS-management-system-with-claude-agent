"""
نموذج تعريف فحص مراقبة قابل لإسناده إلى ملفات المراقبة.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.base import Base
from app.core.utils.datetime import utc_now


class MonitorCommandModel(Base):
    """
    فحص مراقبة مسجل باسمه ونصه ومهلته وطريقة مقارنة مخرجه.
    """
    __tablename__ = "monitor_commands"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )
    fingerprint_strategy: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="canonical_lines",
    )

    fingerprint_config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    command: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    timeout_seconds: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=20.0,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
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
