"""
جزء من Knowledge ingestion/indexing/retrieval لتغذية RAG بمصادر قابلة للتتبع.

الموقع في المعمارية: Application capability / knowledge.
يُستدعى بواسطة: أدوات الإدارة أو Retrieval.
يعتمد مباشرة على: app.infrastructure.database.repositories.knowledge_source_repository.
الحد المعماري: لا يخلط knowledge retrieval مع reasoning.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
    يمثل KnowledgeSourceRuntimeDefinition مسؤولية محددة داخل طبقة Application capability / knowledge.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه أدوات الإدارة أو Retrieval
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى from_model؛ المدخلات المهمة: model.
        تعيد 'KnowledgeSourceRuntimeDefinition' أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يمثل KnowledgeSourceRegistrySnapshot مسؤولية محددة داخل طبقة Application capability / knowledge.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه أدوات الإدارة أو Retrieval
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى find_by_domain؛ المدخلات المهمة: domain.
        تعيد tuple[KnowledgeSourceRuntimeDefinition, ...] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى find_for_specialist؛ المدخلات المهمة: specialist_slug.
        تعيد tuple[KnowledgeSourceRuntimeDefinition, ...] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يمثل KnowledgeSourceRegistry مسؤولية محددة داخل طبقة Application capability / knowledge.

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

    def snapshot(
        self,
    ) -> KnowledgeSourceRegistrySnapshot:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى snapshot؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد KnowledgeSourceRegistrySnapshot أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
