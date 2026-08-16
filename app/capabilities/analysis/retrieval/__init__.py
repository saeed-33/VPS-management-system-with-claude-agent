"""
واجهة مكونات استرجاع سياق التحليل.

تجمع الأنواع والخدمات التي تبحث في التحليلات السابقة وتتحقق من قابليتها للمقارنة
وتحوّل النتائج إلى سياق يمكن للمحلل استخدامه دون اعتباره تشخيصًا حاليًا.
"""

from app.capabilities.analysis.retrieval.reuse_policy import (
    AnalysisDecision,
    AnalysisDecisionResult,
    AnalysisReusePolicy,
)

from app.capabilities.analysis.retrieval.full_text_retriever import (
    FullTextCandidate,
    FullTextQueryBuilder,
    FullTextRetriever,
)

from app.capabilities.analysis.retrieval.hybrid_retriever import HybridRetriever

from app.capabilities.analysis.retrieval.structured_compatibility import (
    CompatibilityConflict,
    CompatibilityResult,
    StructuredCompatibilityChecker,
)
