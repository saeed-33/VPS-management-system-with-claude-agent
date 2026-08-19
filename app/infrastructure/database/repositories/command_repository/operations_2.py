"""
تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها.
"""
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from dataclasses import asdict

from app.infrastructure.database.models.monitor_command import (
    MonitorCommandModel,
)
from app.infrastructure.database.models.profile_command import (
    MonitoringProfileCommandModel,
)
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.commands.command_execution_config import CommandExecutionConfig
from app.core.contracts.commands.create_command_dto import CreateCommandDTO
from app.core.contracts.commands.update_command_dto import UpdateCommandDTO
from app.core.exceptions.command_already_assigned_error import CommandAlreadyAssignedError
from app.core.utils.datetime import utc_now


class _CommandRepositoryMixin2:
    """ينظم مجموعة من عمليات المستودع."""

    def list_enabled_for_server(
        self,
        server_id: int,
    ) -> list[CommandExecutionConfig]:
        """
        يعرض قائمة مرتبة من تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = (
                select(
                    MonitorCommandModel,
                    MonitoringProfileCommandModel,
                )
                .join(
                    MonitoringProfileCommandModel,
                    MonitoringProfileCommandModel.command_id
                    == MonitorCommandModel.id,
                )
                .where(
                    MonitoringProfileCommandModel.server_id
                    == server_id,
                    MonitoringProfileCommandModel.enabled.is_(
                        True
                    ),
                    MonitorCommandModel.enabled.is_(
                        True
                    ),
                )
                .order_by(
                    MonitoringProfileCommandModel.execution_order
                )
            )

            rows = session.execute(statement).all()

            return [
                CommandExecutionConfig(
                    id=command.id,
                    name=command.name,
                    command=command.command,
                    timeout_seconds=(
                        assignment.custom_timeout_seconds
                        if assignment.custom_timeout_seconds
                        is not None
                        else command.timeout_seconds
                    ),
                    execution_order=(
                        assignment.execution_order
                    ),
                )
                for command, assignment in rows
            ]

    def list_assignments_for_server(
        self,
        server_id: int,
    ) -> list[tuple[
        MonitorCommandModel,
        MonitoringProfileCommandModel,
    ]]:
        """
        يعرض قائمة مرتبة من تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = (
                select(
                    MonitorCommandModel,
                    MonitoringProfileCommandModel,
                )
                .join(
                    MonitoringProfileCommandModel,
                    MonitoringProfileCommandModel.command_id
                    == MonitorCommandModel.id,
                )
                .where(
                    MonitoringProfileCommandModel.server_id
                    == server_id
                )
                .order_by(
                    MonitoringProfileCommandModel.execution_order
                )
            )

            return list(
                session.execute(statement).all()
            )
