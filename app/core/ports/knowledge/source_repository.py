"""Port required to manage configured knowledge sources."""
from __future__ import annotations

from typing import Any, Protocol

from app.core.contracts.knowledge_sources.create_knowledge_source_dto import (
    CreateKnowledgeSourceDTO,
)
from app.core.contracts.knowledge_sources.update_knowledge_source_dto import (
    UpdateKnowledgeSourceDTO,
)


class KnowledgeSourceRepositoryPort(Protocol):
    """Persistence operations required by knowledge-source capabilities."""

    def list_all(self) -> list[Any]: ...

    def list_enabled(self) -> list[Any]: ...

    def get_by_id(self, source_id: int) -> Any | None: ...

    def create(self, data: CreateKnowledgeSourceDTO) -> Any: ...

    def update(
        self,
        source_id: int,
        data: UpdateKnowledgeSourceDTO,
    ) -> Any | None: ...

    def set_enabled(self, source_id: int, enabled: bool) -> Any | None: ...

    def delete(self, source_id: int) -> bool: ...
