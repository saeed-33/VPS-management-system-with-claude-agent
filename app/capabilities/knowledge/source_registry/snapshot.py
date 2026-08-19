"""لقطة تشغيلية لمصادر المعرفة."""
from __future__ import annotations
from dataclasses import dataclass
from .runtime_definition import KnowledgeSourceRuntimeDefinition

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
