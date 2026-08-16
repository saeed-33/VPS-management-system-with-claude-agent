"""
خدمة إدارة مصادر المعرفة.

توفر عمليات القراءة والإنشاء والتعديل والتفعيل والحذف عبر مستودع المصادر،
وتحوّل غياب المصدر إلى خطأ واضح للخدمات المستهلكة.
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
    يدير دورة حياة مصدر المعرفة من خلال مستودع المصادر.
    """
    def __init__(
        self,
        repository: KnowledgeSourceRepository,
    ) -> None:
        """
        يربط مستودع مصادر المعرفة بخدمة الإدارة.
        """
        self._repository = repository

    def list_sources(
        self,
        *,
        enabled_only: bool = False,
    ):
        """
        يعيد كل المصادر أو المصادر المفعلة فقط بحسب خيار المستدعي.
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
        يجلب مصدرًا بالمعرف ويرفع خطأ واضحًا عند عدم وجوده.
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
        ينشئ مصدر معرفة جديدًا عبر بيانات العقد المخصصة.
        """
        return self._repository.create(data)

    def update_source(
        self,
        source_id: int,
        data: UpdateKnowledgeSourceDTO,
    ):
        """
        يحدّث مصدرًا موجودًا ويرفع خطأ عند فشل العثور عليه.
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
        يغير تفعيل مصدر المعرفة ويرفع خطأ إذا لم يوجد المصدر.
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
        يحذف مصدر المعرفة ويرفع خطأ إذا لم ينفذ المستودع الحذف.
        """
        if not self._repository.delete(
            source_id
        ):
            raise LookupError(
                "Knowledge source not found."
            )
