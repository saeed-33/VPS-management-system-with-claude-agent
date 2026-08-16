"""
جزء من Monitoring لاختيار profile/commands أو تنفيذ الدورة وحفظ report.

الموقع في المعمارية: Application capability / monitoring.
يُستدعى بواسطة: Scheduler أو MCP أو Admin API.
يعتمد مباشرة على: app.infrastructure.database.models.monitor_command، app.infrastructure.database.models.profile_command، app.infrastructure.database.repositories.command_repository، app.infrastructure.database.repositories.server_repository، app.core.contracts.commands، app.core.exceptions.
الحد المعماري: لا يقوم بتحليل LLM أو Investigation.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from app.infrastructure.database.models.monitor_command import (
    MonitorCommandModel,
)
from app.infrastructure.database.models.profile_command import (
    MonitoringProfileCommandModel,
)
from app.infrastructure.database.repositories.command_repository import (
    CommandRepository,
)
from app.infrastructure.database.repositories.server_repository import (
    ServerRepository,
)
from app.core.contracts.commands import (
    CreateCommandDTO,
    UpdateCommandDTO,
)
from app.core.exceptions import (
    CommandNotFoundError,
    DuplicateCommandError,
    ServerNotFoundError,
)


class CommandService:
    """
    يمثل CommandService مسؤولية محددة داخل طبقة Application capability / monitoring.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Scheduler أو MCP أو Admin API
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        command_repository: CommandRepository,
        server_repository: ServerRepository,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: command_repository، server_repository.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._command_repository = (
            command_repository
        )
        self._server_repository = (
            server_repository
        )

    def list_commands(
        self,
    ) -> list[MonitorCommandModel]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى list_commands؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد list[MonitorCommandModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._command_repository.list_all()

    def get_command(
        self,
        command_id: int,
    ) -> MonitorCommandModel:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى get_command؛ المدخلات المهمة: command_id.
        تعيد MonitorCommandModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        command = (
            self._command_repository.get_by_id(
                command_id
            )
        )

        if command is None:
            raise CommandNotFoundError(command_id)

        return command

    def create_command(
        self,
        data: CreateCommandDTO,
    ) -> MonitorCommandModel:
        """
        ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى create_command؛ المدخلات المهمة: data.
        تعيد MonitorCommandModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._validate_create(data)

        existing = (
            self._command_repository.get_by_name(
                data.name.strip()
            )
        )

        if existing is not None:
            raise DuplicateCommandError(
                data.name
            )

        return self._command_repository.create(
            data
        )

    def update_command(
        self,
        command_id: int,
        data: UpdateCommandDTO,
    ) -> MonitorCommandModel:
        """
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى update_command؛ المدخلات المهمة: command_id، data.
        تعيد MonitorCommandModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        existing = (
            self._command_repository.get_by_id(
                command_id
            )
        )

        if existing is None:
            raise CommandNotFoundError(command_id)

        if (
            data.name is not None
            and data.name.strip() != existing.name
        ):
            duplicate = (
                self._command_repository
                .get_by_name(data.name.strip())
            )

            if duplicate is not None:
                raise DuplicateCommandError(
                    data.name
                )

        updated = (
            self._command_repository.update(
                command_id,
                data,
            )
        )

        if updated is None:
            raise CommandNotFoundError(command_id)

        return updated

    def delete_command(
        self,
        command_id: int,
    ) -> None:
        """
        يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى delete_command؛ المدخلات المهمة: command_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        deleted = (
            self._command_repository.delete(
                command_id
            )
        )

        if not deleted:
            raise CommandNotFoundError(command_id)

    def assign_command_to_server(
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى assign_command_to_server؛ المدخلات المهمة: server_id، command_id، execution_order، enabled، custom_timeout_seconds.
        تعيد MonitoringProfileCommandModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if (
            self._server_repository.get_by_id(
                server_id
            )
            is None
        ):
            raise ServerNotFoundError(server_id)

        if (
            self._command_repository.get_by_id(
                command_id
            )
            is None
        ):
            raise CommandNotFoundError(command_id)

        if execution_order < 1:
            raise ValueError(
                "Execution order must be "
                "greater than zero."
            )

        if (
            custom_timeout_seconds is not None
            and custom_timeout_seconds <= 0
        ):
            raise ValueError(
                "Custom timeout must be "
                "greater than zero."
            )

        return (
            self._command_repository
            .assign_to_server(
                server_id=server_id,
                command_id=command_id,
                execution_order=execution_order,
                enabled=enabled,
                custom_timeout_seconds=(
                    custom_timeout_seconds
                ),
            )
        )

    def remove_command_from_server(
        self,
        *,
        server_id: int,
        command_id: int,
    ) -> None:
        """
        يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى remove_command_from_server؛ المدخلات المهمة: server_id، command_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        removed = (
            self._command_repository
            .remove_from_server(
                server_id=server_id,
                command_id=command_id,
            )
        )

        if not removed:
            raise CommandNotFoundError(command_id)

    @staticmethod
    def _validate_create(
        data: CreateCommandDTO,
    ) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى _validate_create؛ المدخلات المهمة: data.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if not data.name.strip():
            raise ValueError(
                "Command name is required."
            )

        if not data.command.strip():
            raise ValueError(
                "Command text is required."
            )

        if data.timeout_seconds <= 0:
            raise ValueError(
                "Command timeout must be "
                "greater than zero."
            )