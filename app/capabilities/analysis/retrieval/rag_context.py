"""
جزء من Retrieval/RAG لتطبيع report أو استرجاع context أو الفهرسة.

الموقع في المعمارية: Application capability / retrieval.
يُستدعى بواسطة: Analysis orchestrator وخدمات الفهرسة.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: ينتهي عند context مع provenance؛ reasoning مسؤولية أعلى.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievedAnalysisContext:
    """
    يمثل RetrievedAnalysisContext مسؤولية محددة داخل طبقة Application capability / retrieval.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Analysis orchestrator وخدمات الفهرسة
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
