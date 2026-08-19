"""تعريف مصدر معرفة بصيغة تشغيلية."""
from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

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
