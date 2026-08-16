"""
Repository يدير قراءة أو كتابة entity محددة عبر SQLModel/SQLAlchemy.

الموقع في المعمارية: Persistence infrastructure.
يُستدعى بواسطة: application capabilities.
يعتمد مباشرة على: app.infrastructure.database.models.monitor_command، app.infrastructure.database.models.profile_command، app.infrastructure.database.session، app.core.contracts.commands، app.core.exceptions، app.core.utils.datetime.
الحد المعماري: لا يقرر policy أو workflow؛ يحول persistence semantics إلى واجهة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
    يمثل CommandRepository مسؤولية محددة داخل طبقة Persistence infrastructure.

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
        command_id: int,
    ) -> MonitorCommandModel | None:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_id؛ المدخلات المهمة: command_id.
        تعيد MonitorCommandModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى get_by_name؛ المدخلات المهمة: name.
        تعيد MonitorCommandModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_all؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد list[MonitorCommandModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى create؛ المدخلات المهمة: data.
        تعيد MonitorCommandModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        model = MonitorCommandModel(
            name=data.name.strip(),
            command=data.command.strip(),
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى update؛ المدخلات المهمة: command_id، data.
        تعيد MonitorCommandModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى delete؛ المدخلات المهمة: command_id.
        تعيد bool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى assign_to_server؛ المدخلات المهمة: server_id، command_id، execution_order، enabled، custom_timeout_seconds.
        تعيد MonitoringProfileCommandModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى update_server_assignment؛ المدخلات المهمة: server_id، command_id، execution_order، enabled، custom_timeout_seconds.
        تعيد MonitoringProfileCommandModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى remove_from_server؛ المدخلات المهمة: server_id، command_id.
        تعيد bool أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_enabled_for_server؛ المدخلات المهمة: server_id.
        تعيد list[CommandExecutionConfig] أو تحدث الأثر الذي يحدده contract هذه الدالة.
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Persistence infrastructure.

        تُستدعى عندما يصل workflow إلى list_assignments_for_server؛ المدخلات المهمة: server_id.
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