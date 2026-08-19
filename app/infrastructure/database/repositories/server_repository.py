"""
سجلات السيرفرات وحالة المراقبة وإعدادات الاتصال والجدولة.
"""
from datetime import datetime
from dataclasses import asdict
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.server.server import ServerModel
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.servers.create_server_dto import CreateServerDTO
from app.core.contracts.servers.update_server_dto import UpdateServerDTO
from app.core.utils.datetime import utc_now


class ServerRepository:
    """
    مسؤول عن هوية السيرفر وإعداد المراقبة وحالة آخر دورة.
    """
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        """
        يهيئ مستودع سجلات السيرفرات وحالة المراقبة وإعدادات الاتصال والجدولة بمصدر الجلسات الذي سيستخدمه في القراءة والحفظ.
        """
        self._session_factory = session_factory

    def get_by_id(
        self,
        server_id: int,
    ) -> ServerModel | None:
        """
        يسترجع سجلًا من سجلات السيرفرات وحالة المراقبة وإعدادات الاتصال والجدولة بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            return session.get(
                ServerModel,
                server_id,
            )

    def get_by_name(
        self,
        name: str,
    ) -> ServerModel | None:
        """
        يسترجع سجلًا من سجلات السيرفرات وحالة المراقبة وإعدادات الاتصال والجدولة بالمعرف أو المفتاح المطلوب دون اختلاق نتيجة عند غيابه.
        """
        with self._session_factory() as session:
            statement = select(ServerModel).where(
                ServerModel.name == name
            )

            return session.scalar(statement)

    def list_all(self) -> list[ServerModel]:
        """
        يعرض قائمة مرتبة من سجلات السيرفرات وحالة المراقبة وإعدادات الاتصال والجدولة مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = (
                select(ServerModel)
                .order_by(ServerModel.id.desc())
            )

            return list(
                session.scalars(statement).all()
            )

    def list_enabled_servers(
        self,
    ) -> list[ServerModel]:
        """
        يعرض قائمة مرتبة من سجلات السيرفرات وحالة المراقبة وإعدادات الاتصال والجدولة مع إبقاء حدود القراءة واضحة للمرحلة المستدعية.
        """
        with self._session_factory() as session:
            statement = (
                select(ServerModel)
                .where(
                    ServerModel.monitor_enabled.is_(True),
                    ServerModel.monitoring_profile_id.is_not(
                        None
                    ),
                )
                .order_by(ServerModel.id)
            )

            return list(
                session.scalars(statement).all()
            )

    def create(
        self,
        data: CreateServerDTO,
    ) -> ServerModel:
        """
        ينشئ أو يحدث سجلًا في سجلات السيرفرات وحالة المراقبة وإعدادات الاتصال والجدولة ويربطه بالسيرفر أو التقرير أو الخطة المناسبة.
        """
        model = ServerModel(
            name=data.name.strip(),
            host=data.host.strip(),
            port=data.port,
            username=data.username.strip(),
            private_key_path=data.private_key_path,
            description=data.description,
            monitor_enabled=data.monitor_enabled,
            interval_seconds=data.interval_seconds,
        )

        with self._session_factory() as session:
            session.add(model)
            session.commit()
            session.refresh(model)

            return model

    def update(
        self,
        server_id: int,
        data: UpdateServerDTO,
    ) -> ServerModel | None:
        """
        يحدّث انتقالًا أو إعدادًا في سجلات السيرفرات وحالة المراقبة وإعدادات الاتصال والجدولة دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.get(
                ServerModel,
                server_id,
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
        server_id: int,
    ) -> bool:
        """
        يزيل ارتباطًا أو سجلًا من سجلات السيرفرات وحالة المراقبة وإعدادات الاتصال والجدولة بعد تطبيق قواعد الملكية المطلوبة.
        """
        with self._session_factory() as session:
            model = session.get(
                ServerModel,
                server_id,
            )

            if model is None:
                return False

            session.delete(model)
            session.commit()

            return True

    def update_monitoring_status(
        self,
        *,
        server_id: int,
        status: str,
        checked_at: datetime,
        success_at: datetime | None,
        error_message: str | None,
        report_id: int | None,
    ) -> None:
        """
        يحدّث انتقالًا أو إعدادًا في سجلات السيرفرات وحالة المراقبة وإعدادات الاتصال والجدولة دون فقدان السجل السابق المرتبط به.
        """
        with self._session_factory() as session:
            model = session.get(
                ServerModel,
                server_id,
            )

            if model is None:
                return

            model.status = status
            model.last_checked_at = checked_at
            model.last_report_id = report_id
            model.last_error = error_message
            model.updated_at = utc_now()

            if success_at is not None:
                model.last_success_at = success_at

            session.commit()
