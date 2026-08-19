"""مرشح دمج نتائج استرجاع المعرفة."""
from __future__ import annotations
from dataclasses import dataclass
from app.infrastructure.database.repositories.knowledge_retrieval_repository.search_row import KnowledgeSearchRow

@dataclass(slots=True)
class _FusionCandidate:
    """
    يجمع نتائج البحث المتجهي والنصي لمقطع واحد قبل إعادة ترتيبه.
    """
    row: KnowledgeSearchRow
    vector_rank: int | None = None
    vector_score: float | None = None
    text_rank: int | None = None
    text_score: float | None = None

    def rrf_score(self, rrf_k: int) -> float:
        """
        يحسب درجة Reciprocal Rank Fusion للمقطع حسب رتبته في البحث المتجهي والنصي.
        """
        score = 0.0
        if self.vector_rank is not None:
            score += 1.0 / (rrf_k + self.vector_rank)
        if self.text_rank is not None:
            score += 1.0 / (rrf_k + self.text_rank)
        return score

    @property
    def strategy(self) -> str:
        """
        يحدد استراتيجية وصول المقطع: متجهي أو نصي أو هجين.
        """
        if self.vector_rank is not None and self.text_rank is not None:
            return "hybrid"
        if self.vector_rank is not None:
            return "vector"
        return "full_text"
