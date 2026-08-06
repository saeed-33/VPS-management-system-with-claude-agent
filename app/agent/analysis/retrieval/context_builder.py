from typing import Any

from app.agent.analysis.retrieval.rag_context import (
    RetrievedAnalysisContext,
)


class RagContextBuilder:
    def __init__(
        self,
        *,
        max_cases: int = 3,
        max_summary_characters: int = 1200,
        max_issue_characters: int = 1800,
    ) -> None:
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
