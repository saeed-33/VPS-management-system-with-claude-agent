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


class _MonitoringProfileRepositoryMixin1:
    """ينظم مجموعة من عمليات المستودع."""

    def get_by_id(
        self,
        profile_id: int,
    ) -> MonitoringProfileModel | None:
        """
        يسترجع سجلًا من ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.get(
                MonitoringProfileModel,
                profile_id,
            )

    def get_by_name(
        self,
        name: str,
    ) -> MonitoringProfileModel | None:
        """
        يسترجع سجلًا من ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            statement = select(
                MonitoringProfileModel
            ).where(
                MonitoringProfileModel.name == name
            )

            return session.scalar(statement)

    def list_all(
        self,
    ) -> list[MonitoringProfileModel]:
        """
        يعرض قائمة مرتبة من ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = (
                select(MonitoringProfileModel)
                .order_by(
                    MonitoringProfileModel.name
                )
            )

            return list(
                session.scalars(statement).all()
            )

    def create(
        self,
        data: CreateMonitoringProfileDTO,
    ) -> MonitoringProfileModel:
        """
        ينشئ أو يحدث سجلًا في ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = MonitoringProfileModel(
            name=data.name.strip(),
            description=data.description,
            enabled=data.enabled,
        )

        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)

            return model

    def update(
        self,
        profile_id: int,
        data: UpdateMonitoringProfileDTO,
    ) -> MonitoringProfileModel | None:
        """
        يحدّث انتقالًا أو إعدادًا في ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.get(
                MonitoringProfileModel,
                profile_id,
            )

            if model is None:
                return None

            values = {
                key: value
                for key, value in asdict(data).items()
                if value is not None
            }

            for key, value in values.items():
                if isinstance(value, str):
                    value = value.strip()

                setattr(model, key, value)

            model.updated_at = utc_now()

            session.commit()
            session.refresh(model)

            return model

    def delete(
        self,
        profile_id: int,
    ) -> bool:
        """
        يزيل ارتباطًا أو سجلًا من ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها بعد تطبيق قواعد الملكية المطلوبة.
        """
        with self._session_factory() as session:
            model = session.get(
                MonitoringProfileModel,
                profile_id,
            )

            if model is None:
                return False

            session.delete(model)
            session.commit()

            return True

    def assign_command(
        self,
        *,
        profile_id: int,
        command_id: int,
        execution_order: int,
        enabled: bool = True,
        custom_timeout_seconds: (
            float | None
        ) = None,
    ) -> MonitoringProfileCommandModel:
        """
        يربط عنصرًا من ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها بالسيرفر أو الملف أو التحقيق الذي سيستخدمه.
        """
        model = MonitoringProfileCommandModel(
            profile_id=profile_id,
            command_id=command_id,
            execution_order=execution_order,
            enabled=enabled,
            custom_timeout_seconds=(
                custom_timeout_seconds
            ),
        )

        with self._session_factory() as session:
            session.add(model)

            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ValueError(
                    "Command is already assigned "
                    "to this monitoring profile."
                )

            session.refresh(model)

            return model

    def remove_command(
        self,
        *,
        profile_id: int,
        command_id: int,
    ) -> bool:
        """
        يزيل ارتباطًا أو سجلًا من ملفات المراقبة وفحوصها والسيرفرات المرتبطة بها بعد تطبيق قواعد الملكية المطلوبة.
        """
        with self._session_factory() as session:
            statement = delete(
                MonitoringProfileCommandModel
            ).where(
                MonitoringProfileCommandModel.profile_id
                == profile_id,
                MonitoringProfileCommandModel.command_id
                == command_id,
            )

            result = session.execute(statement)
            session.commit()

            return bool(result.rowcount)

    def list_profile_commands(
        self,
        profile_id: int,
    ) -> list[
        tuple[
            MonitorCommandModel,
            MonitoringProfileCommandModel,
        ]
    ]:
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
                .where(
                    MonitoringProfileCommandModel.profile_id
                    == profile_id
                )
                .order_by(
                    MonitoringProfileCommandModel.execution_order
                )
            )

            return list(
                session.execute(statement).all()
            )
