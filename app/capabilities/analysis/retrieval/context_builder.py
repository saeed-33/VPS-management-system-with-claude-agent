"""
جزء من Retrieval/RAG لتطبيع report أو استرجاع context أو الفهرسة.

الموقع في المعمارية: Application capability / retrieval.
يُستدعى بواسطة: Analysis orchestrator وخدمات الفهرسة.
يعتمد مباشرة على: app.capabilities.analysis.retrieval.rag_context.
الحد المعماري: ينتهي عند context مع provenance؛ reasoning مسؤولية أعلى.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from typing import Any

from app.capabilities.analysis.retrieval.rag_context import (
    RetrievedAnalysisContext,
)


class RagContextBuilder:
    """
    يمثل RagContextBuilder مسؤولية محددة داخل طبقة Application capability / retrieval.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Analysis orchestrator وخدمات الفهرسة
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        *,
        max_cases: int = 3,
        max_summary_characters: int = 600,
        max_issue_characters: int = 1000,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: max_cases، max_summary_characters، max_issue_characters.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._max_cases = max_cases
        self._max_summary_characters = (
            max_summary_characters
        )
        self._max_issue_characters = (
            max_issue_characters
        )

    def build(
        self,
        contexts: list[RetrievedAnalysisContext],
    ) -> list[dict[str, Any]]:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى build؛ المدخلات المهمة: contexts.
        تعيد list[dict[str, Any]] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        result: list[dict[str, Any]] = []

        for context in contexts[: self._max_cases]:
            issues = []
            used_characters = 0

            for issue in context.issues:
                item = {
                    "title": issue.get("title"),
                    "severity": issue.get("severity"),
                    "description": issue.get("description"),
                    "evidence": issue.get("evidence"),
                    "recommendation": issue.get(
                        "recommendation"
                    ),
                }
                size = len(str(item))
                if (
                    used_characters + size
                    > self._max_issue_characters
                ):
                    break
                issues.append(item)
                used_characters += size

            result.append(
                {
                    "source_report_id": (
                        context.source_report_id
                    ),
                    "source_analysis_id": (
                        context.source_analysis_id
                    ),
                    "similarity_score": round(
                        context.score,
                        6,
                    ),
                    "rank": context.rank,
                    "retrieval_strategy": (
                        context.retrieval_strategy
                    ),
                    "vector_score": context.vector_score,
                    "text_score": context.text_score,
                    "vector_rank": context.vector_rank,
                    "text_rank": context.text_rank,
                    "health_status": context.health_status,
                    "summary": (
                        context.summary or ""
                    )[: self._max_summary_characters],
                    "issues": issues,
                    "positive_findings": (
                        context.positive_findings[:5]
                    ),
                    "recommended_actions": (
                        context.recommended_actions[:5]
                    ),
                }
            )

        return result
