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
from app.core.contracts.commands import (
    CommandExecutionConfig,
    CreateCommandDTO,
    UpdateCommandDTO,
)
from app.core.exceptions import (
    CommandAlreadyAssignedError,
)
from app.core.utils.datetime import utc_now


class CommandRepository:
    """
    مسؤول عن تعريف فحوص المراقبة وربطها بالسيرفرات وقراءتها بترتيب التنفيذ.
    """
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        """
        يهيئ مستودع تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها بمصدر الجلسات الذي سيستخدمه في القراءة والحفظ.
        """
        self._session_factory = session_factory

    def get_by_id(
        self,
        command_id: int,
    ) -> MonitorCommandModel | None:
        """
        يسترجع سجلًا من تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.get(
                MonitorCommandModel,
                command_id,
            )

    def get_by_name(
        self,
        name: str,
    ) -> MonitorCommandModel | None:
        """
        يسترجع سجلًا من تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            statement = select(
                MonitorCommandModel
            ).where(
                MonitorCommandModel.name == name
            )

            return session.scalar(statement)

    def list_all(
        self,
    ) -> list[MonitorCommandModel]:
        """
        يعرض قائمة مرتبة من تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = (
                select(MonitorCommandModel)
                .order_by(
                    MonitorCommandModel.id.desc()
                )
            )

            return list(
                session.scalars(statement).all()
            )

    def create(
        self,
        data: CreateCommandDTO,
    ) -> MonitorCommandModel:
        """
        ينشئ أو يحدث سجلًا في تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = MonitorCommandModel(
            name=data.name.strip(),
            command=data.command.strip(),
            fingerprint_strategy=data.fingerprint_strategy,
            fingerprint_config=data.fingerprint_config or {},
            description=data.description,
            timeout_seconds=data.timeout_seconds,
            enabled=data.enabled,
        )

        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)

            return model

    def update(
        self,
        command_id: int,
        data: UpdateCommandDTO,
    ) -> MonitorCommandModel | None:
        """
        يحدّث انتقالًا أو إعدادًا في تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.get(
                MonitorCommandModel,
                command_id,
            )

            if model is None:
                return None

            update_values = {
                key: value
                for key, value in asdict(data).items()
                if value is not None
            }

            for key, value in update_values.items():
                if isinstance(value, str):
                    value = value.strip()

                setattr(model, key, value)

            model.updated_at = utc_now()

            session.commit()
            session.refresh(model)

            return model

    def delete(
        self,
        command_id: int,
    ) -> bool:
        """
        يزيل ارتباطًا أو سجلًا من تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها بعد تطبيق قواعد الملكية المطلوبة.
        """
        with self._session_factory() as session:
            model = session.get(
                MonitorCommandModel,
                command_id,
            )

            if model is None:
                return False

            session.delete(model)
            session.commit()

            return True

    def assign_to_server(
        self,
        *,
        server_id: int,
        command_id: int,
        execution_order: int,
        enabled: bool = True,
        custom_timeout_seconds: (
            float | None
        ) = None,
    ) -> MonitoringProfileCommandModel:
        """
        يربط عنصرًا من تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها بالسيرفر أو الملف أو التحقيق الذي سيستخدمه.
        """
        model = MonitoringProfileCommandModel(
            server_id=server_id,
            command_id=command_id,
            execution_order=execution_order,
            enabled=enabled,
            custom_timeout_seconds=(
                custom_timeout_seconds
            ),
        )

        try:
            with self._session_factory() as session:
                session.add(model)
                session.commit()
                session.refresh(model)

                return model

        except IntegrityError as exc:
            raise CommandAlreadyAssignedError(
                server_id=server_id,
                command_id=command_id,
            ) from exc

    def update_server_assignment(
        self,
        *,
        server_id: int,
        command_id: int,
        execution_order: int | None = None,
        enabled: bool | None = None,
        custom_timeout_seconds: (
            float | None
        ) = None,
    ) -> MonitoringProfileCommandModel | None:
        """
        يحدّث انتقالًا أو إعدادًا في تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            statement = select(
                MonitoringProfileCommandModel
            ).where(
                MonitoringProfileCommandModel.server_id
                == server_id,
                MonitoringProfileCommandModel.command_id
                == command_id,
            )

            model = session.scalar(statement)

            if model is None:
                return None

            if execution_order is not None:
                model.execution_order = (
                    execution_order
                )

            if enabled is not None:
                model.enabled = enabled

            model.custom_timeout_seconds = (
                custom_timeout_seconds
            )

            model.updated_at = utc_now()

            session.commit()
            session.refresh(model)

            return model

    def remove_from_server(
        self,
        *,
        server_id: int,
        command_id: int,
    ) -> bool:
        """
        يزيل ارتباطًا أو سجلًا من تعريف فحوص المراقبة وربطها بالسيرفرات وترتيب تنفيذها بعد تطبيق قواعد الملكية المطلوبة.
        """
        with self._session_factory() as session:
            statement = delete(
                MonitoringProfileCommandModel
            ).where(
                MonitoringProfileCommandModel.server_id
                == server_id,
                MonitoringProfileCommandModel.command_id
                == command_id,
            )

            result = session.execute(statement)
            session.commit()

            return bool(result.rowcount)

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
