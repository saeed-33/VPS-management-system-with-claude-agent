"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.infrastructure.database.models.monitor_command، app.infrastructure.database.models.monitoring_profile، app.infrastructure.database.models.profile_command، app.infrastructure.database.models.server، app.infrastructure.database.session، app.core.contracts.profiles.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
from app.infrastructure.database.models.server import (
    ServerModel,
)
from app.infrastructure.database.session import SessionLocal
from app.core.contracts.profiles import (
    CreateMonitoringProfileDTO,
    MonitoringProfileCommandConfig,
    UpdateMonitoringProfileDTO,
)
from app.core.utils.datetime import utc_now


class MonitoringProfileRepository:
    """
    يمثل MonitoringProfileRepository مسؤولية محددة داخل طبقة Persistence infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه application capabilities
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: session_factory.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._session_factory = session_factory

    def get_by_id(
        self,
        profile_id: int,
    ) -> MonitoringProfileModel | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_id؛ المدخلات المهمة: profile_id.
        تعيد MonitoringProfileModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_name؛ المدخلات المهمة: name.
        تعيد MonitoringProfileModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_all؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد list[MonitoringProfileModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى create؛ المدخلات المهمة: data.
        تعيد MonitoringProfileModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى update؛ المدخلات المهمة: profile_id، data.
        تعيد MonitoringProfileModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى delete؛ المدخلات المهمة: profile_id.
        تعيد bool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى assign_command؛ المدخلات المهمة: profile_id، command_id، execution_order، enabled، custom_timeout_seconds.
        تعيد MonitoringProfileCommandModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى remove_command؛ المدخلات المهمة: profile_id، command_id.
        تعيد bool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_profile_commands؛ المدخلات المهمة: profile_id.
        تعيد list[tuple[MonitorCommandModel, MonitoringProfileCommandModel]] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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

    def list_enabled_commands_for_server(
        self,
        server_id: int,
    ) -> list[MonitoringProfileCommandConfig]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_enabled_commands_for_server؛ المدخلات المهمة: server_id.
        تعيد list[MonitoringProfileCommandConfig] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى assign_profile_to_server؛ المدخلات المهمة: server_id، profile_id.
        تعيد ServerModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى update_command_assignment؛ المدخلات المهمة: profile_id، command_id، execution_order، enabled، custom_timeout_seconds، update_custom_timeout.
        تعيد MonitoringProfileCommandModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى count_servers؛ المدخلات المهمة: profile_id.
        تعيد int أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        with self._session_factory() as session:
            statement = select(
                func.count(ServerModel.id)
            ).where(
                ServerModel.monitoring_profile_id
                == profile_id
            )

            return int(session.scalar(statement) or 0)