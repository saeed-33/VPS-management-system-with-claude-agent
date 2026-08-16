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
from enum import StrEnum


class AnalysisDecision(StrEnum):
    """
    يمثل AnalysisDecision مسؤولية محددة داخل طبقة Application capability / retrieval.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Analysis orchestrator وخدمات الفهرسة
    ويعتمد على StrEnum وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    REUSE = "reuse"
    ASSISTED = "assisted"
    FULL = "full"


@dataclass(slots=True, frozen=True)
class AnalysisDecisionResult:
    """
    يمثل AnalysisDecisionResult مسؤولية محددة داخل طبقة Application capability / retrieval.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Analysis orchestrator وخدمات الفهرسة
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    decision: AnalysisDecision
    reason: str


class AnalysisReusePolicy:
    """
    Central policy for selecting the report analysis path.

    Direct reuse remains restricted to exact fingerprint matches.
    Semantic or vector similarity may provide assisted context only.
    """

    def decide(
        self,
        *,
        fingerprint_match: bool,
        historical_context_available: bool,
        assisted_enabled: bool,
        force: bool = False,
    ) -> AnalysisDecisionResult:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى decide؛ المدخلات المهمة: fingerprint_match، historical_context_available، assisted_enabled، force.
        تعيد AnalysisDecisionResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if force:
            return AnalysisDecisionResult(
                decision=AnalysisDecision.FULL,
                reason="forced_analysis",
            )

        if fingerprint_match:
            return AnalysisDecisionResult(
                decision=AnalysisDecision.REUSE,
                reason="exact_fingerprint_match",
            )

        if assisted_enabled and historical_context_available:
            return AnalysisDecisionResult(
                decision=AnalysisDecision.ASSISTED,
                reason="historical_context_available",
            )

        return AnalysisDecisionResult(
            decision=AnalysisDecision.FULL,
            reason="no_usable_historical_context",
        )
