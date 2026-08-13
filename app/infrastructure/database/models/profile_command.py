from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base
from app.shared.utils.datetime import utc_now


class MonitoringProfileCommandModel(Base):
    __tablename__ = "monitoring_profile_commands"

    __table_args__ = (
        UniqueConstraint(
            "profile_id",
            "command_id",
            name="uq_monitoring_profile_command",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    profile_id: Mapped[int] = mapped_column(
        ForeignKey(
            "monitoring_profiles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    command_id: Mapped[int] = mapped_column(
        ForeignKey(
            "monitor_commands.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    execution_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    custom_timeout_seconds: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
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