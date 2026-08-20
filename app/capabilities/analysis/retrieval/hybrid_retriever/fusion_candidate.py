"""مرشح دمج لترتيب نتائج الاسترجاع."""
from __future__ import annotations

from dataclasses import dataclass

from app.core.contracts.analysis.retrieved_analysis_context import RetrievedAnalysisContext

@dataclass(slots=True)
class _FusionCandidate:
    """
    يجمع ترتيب ودرجات مرشح واحد عبر البحث المتجهي والبحث النصي قبل حساب ترتيبه الهجين.
    """
    analysis_id: int
    report_id: int
    vector_rank: int | None = None
    vector_score: float | None = None
    text_rank: int | None = None
    text_score: float | None = None
    vector_context: RetrievedAnalysisContext | None = None

    def rrf_score(self, rrf_k: int) -> float:
        """
        يحسب درجة Reciprocal Rank Fusion من ترتيب المرشح في كل مصدر بحث متاح.
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
        يحدد ما إذا كان المرشح جاء من البحث المتجهي أو النصي أو كليهما.
        """
        if (
            self.vector_rank is not None
            and self.text_rank is not None
        ):
            return "hybrid"

        if self.vector_rank is not None:
            return "vector"

        return "full_text"
