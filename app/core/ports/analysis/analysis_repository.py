"""Port required to persist report-analysis lifecycle and retrieval metadata."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from app.core.contracts.analysis.report_analysis_result import ReportAnalysisResult


class AnalysisRepositoryPort(Protocol):
    """Persistence operations required by analysis capabilities."""

    def get_by_id(self, analysis_id: int) -> Any | None: ...

    def get_by_ids(self, analysis_ids: list[int]) -> dict[int, Any]: ...

    def get_by_report_id(self, report_id: int) -> Any | None: ...

    def create_pending(
        self,
        *,
        report_id: int,
        server_id: int,
        provider_name: str,
        model_name: str,
    ) -> Any: ...

    def mark_running(self, analysis_id: int) -> None: ...

    def mark_completed(
        self,
        *,
        analysis_id: int,
        result: ReportAnalysisResult,
        finished_at: datetime,
        duration_ms: float,
    ) -> None: ...

    def mark_failed(
        self,
        *,
        analysis_id: int,
        error_message: str,
        finished_at: datetime,
        duration_ms: float,
    ) -> None: ...

    def reset_for_retry(self, analysis_id: int) -> None: ...

    def list_pending_or_running(self) -> list[Any]: ...

    def find_completed_by_fingerprint(
        self,
        *,
        server_id: int,
        report_fingerprint: str,
        exclude_report_id: int | None = None,
    ) -> Any | None: ...

    def update_retrieval_metadata(
        self,
        *,
        analysis_id: int,
        report_fingerprint: str,
        normalized_report: str,
        analysis_source: str = "generated",
        reused_from_analysis_id: int | None = None,
        retrieval_strategy: str | None = None,
        retrieval_score: float | None = None,
        llm_called: bool = True,
    ) -> None: ...

    def update_performance_metrics(
        self,
        *,
        analysis_id: int,
        performance_metrics: dict,
    ) -> None: ...

    def create_reused_analysis(
        self,
        *,
        report_id: int,
        server_id: int,
        source_analysis: Any,
        report_fingerprint: str,
        normalized_report: str,
    ) -> Any: ...
