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

from app.shared.database.base import Base
from app.shared.utils.datetime import utc_now


class MonitoringReportModel(Base):
    __tablename__ = "monitoring_reports"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    server_id: Mapped[int] = mapped_column(
        ForeignKey(
            "servers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
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

    connection_successful: Mapped[bool] = (
        mapped_column(
            Boolean,
            nullable=False,
        )
    )

    commands_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    commands_succeeded: Mapped[int] = (
        mapped_column(
            Integer,
            nullable=False,
            default=0,
        )
    )

    commands_failed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    executions: Mapped[
        list["CommandExecutionModel"]
    ] = relationship(
        back_populates="report",
        cascade="all, delete-orphan",
        order_by=(
            "CommandExecutionModel.execution_order"
        ),
        lazy="selectin",
    )


from app.shared.database.models.command_execution import (  # noqa: E402
    CommandExecutionModel,
)