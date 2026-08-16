"""
جزء من Monitoring لاختيار profile/commands أو تنفيذ الدورة وحفظ report.

الموقع في المعمارية: Application capability / monitoring.
يُستدعى بواسطة: Scheduler أو MCP أو Admin API.
يعتمد مباشرة على: app.infrastructure.database.models.monitor_command، app.infrastructure.database.models.monitoring_profile، app.infrastructure.database.models.profile_command، app.infrastructure.database.models.server، app.infrastructure.database.repositories.command_repository، app.infrastructure.database.repositories.profile_repository.
الحد المعماري: لا يقوم بتحليل LLM أو Investigation.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
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
from app.infrastructure.database.repositories.command_repository import (
    CommandRepository,
)
from app.infrastructure.database.repositories.profile_repository import (
    MonitoringProfileRepository,
)
from app.infrastructure.database.repositories.server_repository import (
    ServerRepository,
)
from app.core.contracts.profiles import (
    CreateMonitoringProfileDTO,
    UpdateMonitoringProfileDTO,
)
from app.core.exceptions import (
    CommandNotFoundError,
    DuplicateMonitoringProfileError,
    MonitoringProfileNotFoundError,
    ProfileCommandNotFoundError,
    ServerNotFoundError,
)


class MonitoringProfileService:
    """
    يمثل MonitoringProfileService مسؤولية محددة داخل طبقة Application capability / monitoring.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Scheduler أو MCP أو Admin API
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        *,
        profile_repository: MonitoringProfileRepository,
        command_repository: CommandRepository,
        server_repository: ServerRepository,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: profile_repository، command_repository، server_repository.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._profile_repository = profile_repository
        self._command_repository = command_repository
        self._server_repository = server_repository

    def list_profiles(
        self,
    ) -> list[MonitoringProfileModel]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى list_profiles؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد list[MonitoringProfileModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._profile_repository.list_all()

    def get_profile(
        self,
        profile_id: int,
    ) -> MonitoringProfileModel:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى get_profile؛ المدخلات المهمة: profile_id.
        تعيد MonitoringProfileModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        profile = self._profile_repository.get_by_id(
            profile_id
        )

        if profile is None:
            raise MonitoringProfileNotFoundError(
                profile_id
            )

        return profile

    def create_profile(
        self,
        data: CreateMonitoringProfileDTO,
    ) -> MonitoringProfileModel:
        """
        ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى create_profile؛ المدخلات المهمة: data.
        تعيد MonitoringProfileModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if not data.name.strip():
            raise ValueError(
                "Monitoring profile name is required."
            )

        existing = self._profile_repository.get_by_name(
            data.name.strip()
        )

        if existing is not None:
            raise DuplicateMonitoringProfileError(
                data.name
            )

        return self._profile_repository.create(data)

    def update_profile(
        self,
        profile_id: int,
        data: UpdateMonitoringProfileDTO,
    ) -> MonitoringProfileModel:
        """
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى update_profile؛ المدخلات المهمة: profile_id، data.
        تعيد MonitoringProfileModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        current = self.get_profile(profile_id)

        if (
            data.name is not None
            and data.name.strip() != current.name
        ):
            duplicate = (
                self._profile_repository.get_by_name(
                    data.name.strip()
                )
            )

            if duplicate is not None:
                raise DuplicateMonitoringProfileError(
                    data.name
                )

        updated = self._profile_repository.update(
            profile_id,
            data,
        )

        if updated is None:
            raise MonitoringProfileNotFoundError(
                profile_id
            )

        return updated

    def delete_profile(
        self,
        profile_id: int,
    ) -> None:
        """
        يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى delete_profile؛ المدخلات المهمة: profile_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        deleted = self._profile_repository.delete(
            profile_id
        )

        if not deleted:
            raise MonitoringProfileNotFoundError(
                profile_id
            )

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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى list_profile_commands؛ المدخلات المهمة: profile_id.
        تعيد list[tuple[MonitorCommandModel, MonitoringProfileCommandModel]] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self.get_profile(profile_id)

        return (
            self._profile_repository
            .list_profile_commands(profile_id)
        )

    def assign_command(
        self,
        *,
        profile_id: int,
        command_id: int,
        execution_order: int,
        enabled: bool,
        custom_timeout_seconds: float | None,
    ) -> MonitoringProfileCommandModel:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى assign_command؛ المدخلات المهمة: profile_id، command_id، execution_order، enabled، custom_timeout_seconds.
        تعيد MonitoringProfileCommandModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self.get_profile(profile_id)

        command = self._command_repository.get_by_id(
            command_id
        )

        if command is None:
            raise CommandNotFoundError(command_id)

        if execution_order < 1:
            raise ValueError(
                "Execution order must be greater "
                "than zero."
            )

        return self._profile_repository.assign_command(
            profile_id=profile_id,
            command_id=command_id,
            execution_order=execution_order,
            enabled=enabled,
            custom_timeout_seconds=(
                custom_timeout_seconds
            ),
        )

    def update_command_assignment(
        self,
        *,
        profile_id: int,
        command_id: int,
        execution_order: int | None,
        enabled: bool | None,
        custom_timeout_seconds: float | None,
        update_custom_timeout: bool,
    ) -> MonitoringProfileCommandModel:
        """
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى update_command_assignment؛ المدخلات المهمة: profile_id، command_id، execution_order، enabled، custom_timeout_seconds، update_custom_timeout.
        تعيد MonitoringProfileCommandModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self.get_profile(profile_id)

        updated = (
            self._profile_repository
            .update_command_assignment(
                profile_id=profile_id,
                command_id=command_id,
                execution_order=execution_order,
                enabled=enabled,
                custom_timeout_seconds=(
                    custom_timeout_seconds
                ),
                update_custom_timeout=(
                    update_custom_timeout
                ),
            )
        )

        if updated is None:
            raise ProfileCommandNotFoundError(
                profile_id,
                command_id,
            )

        return updated

    def remove_command(
        self,
        *,
        profile_id: int,
        command_id: int,
    ) -> None:
        """
        يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى remove_command؛ المدخلات المهمة: profile_id، command_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        removed = (
            self._profile_repository.remove_command(
                profile_id=profile_id,
                command_id=command_id,
            )
        )

        if not removed:
            raise ProfileCommandNotFoundError(
                profile_id,
                command_id,
            )

    def assign_profile_to_server(
        self,
        *,
        server_id: int,
        profile_id: int | None,
    ) -> ServerModel:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى assign_profile_to_server؛ المدخلات المهمة: server_id، profile_id.
        تعيد ServerModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if (
            self._server_repository.get_by_id(server_id)
            is None
        ):
            raise ServerNotFoundError(server_id)

        if profile_id is not None:
            self.get_profile(profile_id)

        server = (
            self._profile_repository
            .assign_profile_to_server(
                server_id=server_id,
                profile_id=profile_id,
            )
        )

        if server is None:
            raise ServerNotFoundError(server_id)

        return server