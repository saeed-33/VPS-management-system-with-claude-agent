"""
نموذج السياق المسترجع من تحليل تاريخي.

يحمل هوية التقرير والتحليل المصدرين ودرجات البحث وترتيبه والنتائج التشغيلية
التي يمكن عرضها للمحلل مع تحديد استراتيجية الاسترجاع المستخدمة.
"""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievedAnalysisContext:
    """
    يمثل التحليل التاريخي المقبول كسياق مع مصادره ودرجاته ونتائجه التشغيلية.
    """
    source_report_id: int
    source_analysis_id: int
    score: float
    rank: int
    health_status: str | None
    summary: str | None
    issues: list[dict]
    positive_findings: list[str]
    recommended_actions: list[str]
    retrieval_strategy: str = "vector"
    vector_score: float | None = None
    text_score: float | None = None
    vector_rank: int | None = None
    text_rank: int | None = None
