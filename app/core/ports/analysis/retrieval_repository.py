"""Port required to index and search analyzed reports."""
from __future__ import annotations

from typing import Any, Protocol


class AnalysisRetrievalRepositoryPort(Protocol):
    """Persistence operations for report retrieval documents."""

    def upsert_document(
        self,
        *,
        report_id: int,
        analysis_id: int,
        server_id: int,
        monitoring_profile_id: int | None,
        command_set_hash: str | None,
        connection_successful: bool | None,
        failed_command_ids: list[int],
        error_signatures: list[str],
        fingerprint: str,
        normalized_text: str,
        structured_features: dict,
        embedding: list[float],
        embedding_provider: str,
        embedding_model: str,
        embedding_dimensions: int,
        analysis_health_status: str | None,
    ) -> Any: ...

    def clone_document(
        self,
        *,
        source_analysis_id: int,
        target_analysis_id: int,
        target_report_id: int,
        target_server_id: int,
        target_fingerprint: str,
        target_normalized_text: str,
        target_health_status: str | None,
    ) -> Any | None: ...

    def get_by_analysis_id(self, analysis_id: int) -> Any | None: ...

    def find_by_full_text(
        self,
        *,
        query_text: str,
        server_id: int,
        monitoring_profile_id: int | None,
        command_set_hash: str | None,
        exclude_report_id: int | None = None,
        minimum_rank: float = 0.0,
        limit: int = 20,
    ) -> list[tuple[Any, float]]: ...

    def find_similar(
        self,
        *,
        server_id: int,
        monitoring_profile_id: int | None,
        command_set_hash: str | None,
        embedding: list[float],
        exclude_report_id: int | None = None,
        minimum_score: float = 0.0,
        limit: int = 5,
        hnsw_ef_search: int = 100,
    ) -> list[tuple[Any, float]]: ...
