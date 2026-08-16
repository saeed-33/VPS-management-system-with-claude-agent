"""
جزء من Knowledge ingestion/indexing/retrieval لتغذية RAG بمصادر قابلة للتتبع.

الموقع في المعمارية: Application capability / knowledge.
يُستدعى بواسطة: أدوات الإدارة أو Retrieval.
يعتمد مباشرة على: app.infrastructure.database.repositories.knowledge_source_repository، app.core.contracts.knowledge_sources.
الحد المعماري: لا يخلط knowledge retrieval مع reasoning.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from app.infrastructure.database.repositories.knowledge_source_repository import (
    KnowledgeSourceRepository,
)
from app.core.contracts.knowledge_sources import (
    CreateKnowledgeSourceDTO,
    UpdateKnowledgeSourceDTO,
)


class KnowledgeSourceService:
    """
    يمثل KnowledgeSourceService مسؤولية محددة داخل طبقة Application capability / knowledge.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه أدوات الإدارة أو Retrieval
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        repository: KnowledgeSourceRepository,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: repository.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._repository = repository

    def list_sources(
        self,
        *,
        enabled_only: bool = False,
    ):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى list_sources؛ المدخلات المهمة: enabled_only.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if enabled_only:
            return (
                self._repository
                .list_enabled()
            )

        return self._repository.list_all()

    def get_source(
        self,
        source_id: int,
    ):
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى get_source؛ المدخلات المهمة: source_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        source = self._repository.get_by_id(
            source_id
        )

        if source is None:
            raise LookupError(
                "Knowledge source not found."
            )

        return source

    def create_source(
        self,
        data: CreateKnowledgeSourceDTO,
    ):
        """
        ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى create_source؛ المدخلات المهمة: data.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.create(data)

    def update_source(
        self,
        source_id: int,
        data: UpdateKnowledgeSourceDTO,
    ):
        """
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى update_source؛ المدخلات المهمة: source_id، data.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        source = self._repository.update(
            source_id,
            data,
        )

        if source is None:
            raise LookupError(
                "Knowledge source not found."
            )

        return source

    def set_enabled(
        self,
        source_id: int,
        enabled: bool,
    ):
        """
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى set_enabled؛ المدخلات المهمة: source_id، enabled.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        source = (
            self._repository
            .set_enabled(
                source_id,
                enabled,
            )
        )

        if source is None:
            raise LookupError(
                "Knowledge source not found."
            )

        return source

    def delete_source(
        self,
        source_id: int,
    ) -> None:
        """
        يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى delete_source؛ المدخلات المهمة: source_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if not self._repository.delete(
            source_id
        ):
            raise LookupError(
                "Knowledge source not found."
            )
