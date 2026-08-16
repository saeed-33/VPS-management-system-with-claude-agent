"""
تحويل نتائج الاسترجاع إلى سياق صالح لمطالبة التحليل.

يختار الحقول المفيدة من التحليلات السابقة ويضع حدودًا للحجم، مع إبقاء مصدر كل
قرينة ودرجتها واضحين حتى لا تختلط الخبرة التاريخية بدليل التقرير الحالي.
"""
from typing import Any

from app.capabilities.analysis.retrieval.rag_context import (
    RetrievedAnalysisContext,
)


class RagContextBuilder:
    """
    يبني قائمة سياق مختصرة ومنظمة من نتائج التحليلات المسترجعة لإدراجها في مطالبة النموذج.
    """
    def __init__(
        self,
        *,
        max_cases: int = 3,
        max_summary_characters: int = 600,
        max_issue_characters: int = 1000,
    ) -> None:
        """
        يحفظ الحد الأقصى لعدد السياقات وطول كل سياق المستخدم عند بناء المطالبة.
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
        يحوّل السياقات المسترجعة إلى سجلات موجزة تشمل المصدر والدرجات والنتائج، ثم يحد العدد والحجم.
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
