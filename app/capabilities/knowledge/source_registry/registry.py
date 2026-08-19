"""إنشاء لقطات تشغيلية من مستودع مصادر المعرفة."""
from __future__ import annotations
from app.infrastructure.database.repositories.knowledge_source_repository import KnowledgeSourceRepository
from .runtime_definition import KnowledgeSourceRuntimeDefinition
from .snapshot import KnowledgeSourceRegistrySnapshot

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
