"""
جزء من Investigation/Specialist لتوجيه التحقيق وجمع Evidence وبناء التشخيص.

الموقع في المعمارية: Application capability / investigation.
يُستدعى بواسطة: MCP أو Analysis workflow.
يعتمد مباشرة على: app.infrastructure.database.models.specialist_definition، app.infrastructure.database.repositories.specialist_definition_repository، app.core.contracts.specialists، app.core.exceptions.
الحد المعماري: لا يتجاوز Diagnostic Policy؛ Python يتحقق وينفذ collection.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from app.infrastructure.database.models.specialist_definition import (
    SpecialistDefinitionModel,
)
from app.infrastructure.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)
from app.core.contracts.specialists import (
    CreateSpecialistDefinitionDTO,
    UpdateSpecialistDefinitionDTO,
)
from app.core.exceptions import (
    DuplicateSpecialistDefinitionError,
    SpecialistDefinitionNotFoundError,
)


class SpecialistDefinitionService:
    """
    يمثل SpecialistDefinitionService مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        repository: SpecialistDefinitionRepository,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: repository.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._repository = repository

    def list_specialists(
        self,
        *,
        enabled_only: bool = False,
    ) -> list[SpecialistDefinitionModel]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى list_specialists؛ المدخلات المهمة: enabled_only.
        تعيد list[SpecialistDefinitionModel] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if enabled_only:
            return self._repository.list_enabled()

        return self._repository.list_all()

    def get_specialist(
        self,
        specialist_id: int,
    ) -> SpecialistDefinitionModel:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى get_specialist؛ المدخلات المهمة: specialist_id.
        تعيد SpecialistDefinitionModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        specialist = self._repository.get_by_id(
            specialist_id
        )

        if specialist is None:
            raise SpecialistDefinitionNotFoundError(
                specialist_id
            )

        return specialist

    def create_specialist(
        self,
        data: CreateSpecialistDefinitionDTO,
    ) -> SpecialistDefinitionModel:
        """
        ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى create_specialist؛ المدخلات المهمة: data.
        تعيد SpecialistDefinitionModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        slug = data.slug.strip().lower()

        if self._repository.get_by_slug(slug) is not None:
            raise DuplicateSpecialistDefinitionError(
                slug
            )

        try:
            return self._repository.create(data)
        except ValueError as exc:
            if "slug already exists" in str(exc):
                raise DuplicateSpecialistDefinitionError(
                    slug
                ) from exc
            raise

    def update_specialist(
        self,
        specialist_id: int,
        data: UpdateSpecialistDefinitionDTO,
    ) -> SpecialistDefinitionModel:
        """
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى update_specialist؛ المدخلات المهمة: specialist_id، data.
        تعيد SpecialistDefinitionModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self.get_specialist(specialist_id)

        updated = self._repository.update(
            specialist_id,
            data,
        )

        if updated is None:
            raise SpecialistDefinitionNotFoundError(
                specialist_id
            )

        return updated

    def set_enabled(
        self,
        specialist_id: int,
        enabled: bool,
    ) -> SpecialistDefinitionModel:
        """
        يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى set_enabled؛ المدخلات المهمة: specialist_id، enabled.
        تعيد SpecialistDefinitionModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        updated = self._repository.set_enabled(
            specialist_id,
            enabled,
        )

        if updated is None:
            raise SpecialistDefinitionNotFoundError(
                specialist_id
            )

        return updated

    def delete_specialist(
        self,
        specialist_id: int,
    ) -> None:
        """
        يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى delete_specialist؛ المدخلات المهمة: specialist_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if not self._repository.delete(
            specialist_id
        ):
            raise SpecialistDefinitionNotFoundError(
                specialist_id
            )
