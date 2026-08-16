"""
إنشاء لقطة تشغيلية من مصادر المعرفة المفعلة.

يحوّل نماذج قاعدة البيانات إلى تعريفات غير قابلة للتعديل، ويرتبها حسب الأولوية
ويوفر بحثًا سريعًا بالمجال أو بمعرف الاختصاص.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from app.infrastructure.database.repositories.knowledge_source_repository import (
    KnowledgeSourceRepository,
)


@dataclass(slots=True, frozen=True)
class KnowledgeSourceRuntimeDefinition:
    """
    يمثل تعريف مصدر معرفة مفعّلًا بصيغة تشغيلية مطبعة وقابلة للقراءة.
    """
    id: int
    slug: str
    name: str
    description: str | None
    source_type: str
    source_uri: str | None
    inline_content: str | None
    domains: tuple[str, ...]
    specialist_slugs: tuple[str, ...]
    tags: tuple[str, ...]
    priority: int
    metadata: Mapping[str, object]

    @classmethod
    def from_model(
        cls,
        model,
    ) -> "KnowledgeSourceRuntimeDefinition":
        """
        يحوّل نموذج قاعدة البيانات إلى تعريف تشغيل مطبع مع قوائم المجالات والاختصاصات والوسوم.
        """
        return cls(
            id=model.id,
            slug=model.slug.strip().lower(),
            name=model.name.strip(),
            description=model.description,
            source_type=(
                model.source_type
                .strip()
                .lower()
            ),
            source_uri=model.source_uri,
            inline_content=(
                model.inline_content
            ),
            domains=tuple(
                str(value).strip().casefold()
                for value in model.domains
                if str(value).strip()
            ),
            specialist_slugs=tuple(
                str(value).strip().casefold()
                for value
                in model.specialist_slugs
                if str(value).strip()
            ),
            tags=tuple(
                str(value).strip().casefold()
                for value in model.tags
                if str(value).strip()
            ),
            priority=model.priority,
            metadata=MappingProxyType(
                dict(
                    model.source_metadata
                )
            ),
        )


@dataclass(slots=True, frozen=True)
class KnowledgeSourceRegistrySnapshot:
    """
    يلتقط مجموعة المصادر المفعلة ويوفر البحث فيها بالمجال أو الاختصاص.
    """
    sources: tuple[
        KnowledgeSourceRuntimeDefinition,
        ...
    ]

    def find_by_domain(
        self,
        domain: str,
    ) -> tuple[
        KnowledgeSourceRuntimeDefinition,
        ...
    ]:
        """
        يعيد المصادر التي تعلن ارتباطها بالمجال المطلوب بعد تطبيع الاسم.
        """
        value = domain.strip().casefold()

        if not value:
            return ()

        return tuple(
            source
            for source in self.sources
            if value in source.domains
        )

    def find_for_specialist(
        self,
        specialist_slug: str,
    ) -> tuple[
        KnowledgeSourceRuntimeDefinition,
        ...
    ]:
        """
        يعيد المصادر المرتبطة بمعرف الاختصاص المطلوب بعد تطبيع الاسم.
        """
        value = (
            specialist_slug
            .strip()
            .casefold()
        )

        if not value:
            return ()

        return tuple(
            source
            for source in self.sources
            if value
            in source.specialist_slugs
        )


class KnowledgeSourceRegistry:
    """
    يبني لقطات تشغيلية مرتبة من مستودع مصادر المعرفة.
    """
    def __init__(
        self,
        repository: KnowledgeSourceRepository,
    ) -> None:
        """
        يحفظ مستودع مصادر المعرفة الذي ستبنى منه اللقطات.
        """
        self._repository = repository

    def snapshot(
        self,
    ) -> KnowledgeSourceRegistrySnapshot:
        """
        يقرأ المصادر المفعلة ويحولها إلى تعريفات مرتبة داخل لقطة غير قابلة للتغيير.
        """
        sources = tuple(
            sorted(
                (
                    KnowledgeSourceRuntimeDefinition
                    .from_model(model)
                    for model
                    in self._repository
                    .list_enabled()
                ),
                key=lambda item: (
                    item.priority,
                    item.name.casefold(),
                    item.slug,
                    item.id,
                ),
            )
        )

        return KnowledgeSourceRegistrySnapshot(
            sources=sources
        )
