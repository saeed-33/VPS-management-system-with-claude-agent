"""Port required to persist analysis provenance sources."""
from __future__ import annotations

from typing import Any, Protocol


class AnalysisSourceRepositoryPort(Protocol):
    """Persistence operations for analysis source provenance."""

    def replace_for_analysis(
        self,
        *,
        analysis_id: int,
        sources: list[dict],
    ) -> None: ...

    def list_by_analysis_id(self, analysis_id: int) -> list[Any]: ...
