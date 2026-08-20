"""
إدارة تعريفات الاختصاصيين.

توفر الخدمة عمليات القراءة والإنشاء والتعديل والتفعيل والحذف عبر المستودع،
وتتحقق من الروابط والسياسات قبل إعادة العقد للواجهات.
"""
from __future__ import annotations

from typing import Any

from app.core.ports.investigation.specialist_definition_repository import (
    SpecialistDefinitionRepositoryPort,
)
from app.core.contracts.specialists.create_specialist_definition_dto import CreateSpecialistDefinitionDTO
from app.core.contracts.specialists.update_specialist_definition_dto import UpdateSpecialistDefinitionDTO
from app.core.exceptions.duplicate_specialist_definition_error import DuplicateSpecialistDefinitionError
from app.core.exceptions.specialist_definition_not_found_error import SpecialistDefinitionNotFoundError


class SpecialistDefinitionService:
    """
    يدير تعريفات الاختصاصيين عبر مستودعها.
    """
    def __init__(
        self,
        repository: SpecialistDefinitionRepositoryPort,
    ) -> None:
        """
        يهيئ SpecialistDefinitionService ويربط الاعتماديات اللازمة لدورة التحقيق.
        """
        self._repository = repository

    def list_specialists(
        self,
        *,
        enabled_only: bool = False,
    ) -> list[Any]:
        """
        يعرض تعريفات الاختصاصيين مع خيار الاقتصار على المفعلة.
        """
        if enabled_only:
            return self._repository.list_enabled()

        return self._repository.list_all()

    def get_specialist(
        self,
        specialist_id: int,
    ) -> Any:
        """
        يجلب تعريف اختصاصي ويرفع خطأ عند غيابه.
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
    ) -> Any:
        """
        ينشئ تعريف اختصاصي بعد التحقق من الحقول والروابط.
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
    ) -> Any:
        """
        يحدّث تعريف اختصاصي موجودًا.
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
    ) -> Any:
        """
        يغير حالة تفعيل الاختصاصي.
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
        يحذف تعريف الاختصاصي.
        """
        if not self._repository.delete(
            specialist_id
        ):
            raise SpecialistDefinitionNotFoundError(
                specialist_id
            )
