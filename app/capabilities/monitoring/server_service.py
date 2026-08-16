"""
جزء من Monitoring لاختيار profile/commands أو تنفيذ الدورة وحفظ report.

الموقع في المعمارية: Application capability / monitoring.
يُستدعى بواسطة: Scheduler أو MCP أو Admin API.
يعتمد مباشرة على: app.infrastructure.database.models.server، app.infrastructure.database.repositories.server_repository، app.core.contracts.servers، app.core.exceptions.
الحد المعماري: لا يقوم بتحليل LLM أو Investigation.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from app.infrastructure.database.models.server import (
    ServerModel,
)
from app.infrastructure.database.repositories.server_repository import (
    ServerRepository,
)
from app.core.contracts.servers import (
    CreateServerDTO,
    UpdateServerDTO,
)
from app.core.exceptions import (
    DuplicateServerError,
    ServerNotFoundError,
)


class ServerService:
    """
    يمثل ServerService مسؤولية محددة داخل طبقة Application capability / monitoring.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Scheduler أو MCP أو Admin API
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        repository: ServerRepository,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: repository.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._repository = repository

    def list_servers(self) -> list[ServerModel]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى list_servers؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد list[ServerModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.list_all()

    def get_server(
        self,
        server_id: int,
    ) -> ServerModel:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى get_server؛ المدخلات المهمة: server_id.
        تعيد ServerModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        server = self._repository.get_by_id(
            server_id
        )

        if server is None:
            raise ServerNotFoundError(server_id)

        return server

    def create_server(
        self,
        data: CreateServerDTO,
    ) -> ServerModel:
        """
        ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى create_server؛ المدخلات المهمة: data.
        تعيد ServerModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._validate_create(data)

        existing = self._repository.get_by_name(
            data.name.strip()
        )

        if existing is not None:
            raise DuplicateServerError(data.name)

        return self._repository.create(data)

    def update_server(
        self,
        server_id: int,
        data: UpdateServerDTO,
    ) -> ServerModel:
        """
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى update_server؛ المدخلات المهمة: server_id، data.
        تعيد ServerModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        existing = self._repository.get_by_id(
            server_id
        )

        if existing is None:
            raise ServerNotFoundError(server_id)

        if (
            data.name is not None
            and data.name.strip() != existing.name
        ):
            duplicate = (
                self._repository.get_by_name(
                    data.name.strip()
                )
            )

            if duplicate is not None:
                raise DuplicateServerError(
                    data.name
                )

        updated = self._repository.update(
            server_id,
            data,
        )

        if updated is None:
            raise ServerNotFoundError(server_id)

        return updated

    def delete_server(
        self,
        server_id: int,
    ) -> None:
        """
        يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى delete_server؛ المدخلات المهمة: server_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        deleted = self._repository.delete(
            server_id
        )

        if not deleted:
            raise ServerNotFoundError(server_id)

    @staticmethod
    def _validate_create(
        data: CreateServerDTO,
    ) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / monitoring.

        تُستدعى عندما يصل workflow إلى _validate_create؛ المدخلات المهمة: data.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if not data.name.strip():
            raise ValueError(
                "Server name is required."
            )

        if not data.host.strip():
            raise ValueError(
                "Server host is required."
            )

        if not data.username.strip():
            raise ValueError(
                "SSH username is required."
            )

        if not 1 <= data.port <= 65535:
            raise ValueError(
                "SSH port must be between "
                "1 and 65535."
            )

        if data.interval_seconds < 5:
            raise ValueError(
                "Monitoring interval must be "
                "at least 5 seconds."
            )