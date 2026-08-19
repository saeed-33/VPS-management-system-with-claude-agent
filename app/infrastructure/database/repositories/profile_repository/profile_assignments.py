"""
ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها.
"""
from dataclasses import asdict
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.monitor_command import (
    MonitorCommandModel,
)
from app.infrastructure.database.models.monitoring_profile import (
    MonitoringProfileModel,
)
from app.infrastructure.database.models.profile_command import (
    MonitoringProfileCommandModel,
)
from app.infrastructure.database.models.server.server import ServerModel
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.profiles.create_monitoring_profile_dto import CreateMonitoringProfileDTO
from app.core.contracts.profiles.monitoring_profile_command_config import MonitoringProfileCommandConfig
from app.core.contracts.profiles.update_monitoring_profile_dto import UpdateMonitoringProfileDTO
from app.core.utils.datetime import utc_now


class _ProfileAssignmentsMixin:
    """ينظم مجموعة من عمليات المستودع."""

    def list_enabled_commands_for_server(
        self,
        server_id: int,
    ) -> list[MonitoringProfileCommandConfig]:
        """
        يعرض قائمة مرتبة من ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
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
                .join(
                    MonitoringProfileModel,
                    MonitoringProfileModel.id
                    == MonitoringProfileCommandModel.profile_id,
                )
                .join(
                    ServerModel,
                    ServerModel.monitoring_profile_id
                    == MonitoringProfileModel.id,
                )
                .where(
                    ServerModel.id == server_id,
                    MonitoringProfileModel.enabled.is_(
                        True
                    ),
                    MonitorCommandModel.enabled.is_(
                        True
                    ),
                    MonitoringProfileCommandModel.enabled.is_(
                        True
                    ),
                )
                .order_by(
                    MonitoringProfileCommandModel.execution_order
                )
            )

            rows = session.execute(statement).all()

            return [
                MonitoringProfileCommandConfig(
                    id=command.id,
                    name=command.name,
                    command=command.command,

                    timeout_seconds=(
                        profile_command.custom_timeout_seconds
                        if profile_command.custom_timeout_seconds
                        is not None
                        else command.timeout_seconds
                    ),

                    execution_order=(
                        profile_command.execution_order
                    ),

                    fingerprint_strategy=(
                        command.fingerprint_strategy
                    ),

                    fingerprint_config=(
                        command.fingerprint_config
                        or {}
                    ),
                )
                for command, profile_command in rows
            ]

    def assign_profile_to_server(
        self,
        *,
        server_id: int,
        profile_id: int | None,
    ) -> ServerModel | None:
        """
        يربط عنصرًا من ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها بالسيرفر أو الملف أو التحقيق الذي سيستخدمه.
        """
        with self._session_factory() as session:
            server = session.get(
                ServerModel,
                server_id,
            )

            if server is None:
                return None
            
            if profile_id is not None:
                profile = session.get(
                    MonitoringProfileModel,
                    profile_id,
                )

                if profile is None:
                    raise ValueError(
                        "Monitoring profile does not exist."
                    )

            server.monitoring_profile_id = profile_id
            server.updated_at = utc_now()

            session.commit()
            session.refresh(server)

            return server

    def update_command_assignment(
        self,
        *,
        profile_id: int,
        command_id: int,
        execution_order: int | None = None,
        enabled: bool | None = None,
        custom_timeout_seconds: float | None = None,
        update_custom_timeout: bool = False,
    ) -> MonitoringProfileCommandModel | None:
        """
        يحدّث انتقالًا أو إعدادًا في ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            statement = select(
                MonitoringProfileCommandModel
            ).where(
                MonitoringProfileCommandModel.profile_id
                == profile_id,
                MonitoringProfileCommandModel.command_id
                == command_id,
            )

            model = session.scalar(statement)

            if model is None:
                return None

            if execution_order is not None:
                model.execution_order = execution_order

            if enabled is not None:
                model.enabled = enabled

            if update_custom_timeout:
                model.custom_timeout_seconds = (
                    custom_timeout_seconds
                )

            model.updated_at = utc_now()

            session.commit()
            session.refresh(model)

        return model

    def count_servers(
        self,
        profile_id: int,
    ) -> int:
        """
        يحسب عدد سجلات ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها اللازمة لعرض الحالة أو تطبيق حد من حدودها.
        """
        with self._session_factory() as session:
            statement = select(
                func.count(ServerModel.id)
            ).where(
                ServerModel.monitoring_profile_id
                == profile_id
            )

            return int(session.scalar(statement) or 0)
