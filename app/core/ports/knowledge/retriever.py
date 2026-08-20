"""Port used by investigation to retrieve technical knowledge."""
from __future__ import annotations

from typing import Protocol

from app.core.contracts.knowledge_sources.knowledge_retrieval_context import (
    KnowledgeRetrievalContext,
)


class KnowledgeRetrieverPort(Protocol):
    """واجهة استرجاع المعرفة التي تحتاجها طبقة التحقيق."""

    async def retrieve(
        self,
        *,
        query: str,
        specialist_slug: str | None = None,
        domains: tuple[str, ...] = (),
    ) -> list[KnowledgeRetrievalContext]: ...
