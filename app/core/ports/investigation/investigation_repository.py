"""Port required to persist investigation state and specialist execution."""
from __future__ import annotations

from typing import Any, Callable, Protocol

from app.core.contracts.investigations.persist_investigation_dto import (
    PersistInvestigationDTO,
)


class InvestigationRepositoryPort(Protocol):
    """Persistence operations required by investigation capabilities."""

    def create(self, data: PersistInvestigationDTO) -> Any: ...

    def get_by_investigation_id(self, investigation_id: str) -> Any | None: ...

    def list_by_report_id(self, report_id: int) -> list[Any]: ...

    def list_recent(
        self,
        *,
        limit: int = 100,
        server_id: int | None = None,
    ) -> list[Any]: ...

    def list_recoverable(self, *, limit: int = 1) -> list[Any]: ...

    def update_runtime_snapshot(
        self,
        *,
        investigation_id: str,
        status: str,
        metadata: dict,
    ) -> Any: ...

    def merge_runtime_snapshot(
        self,
        *,
        investigation_id: str,
        status: str,
        merge: Callable[[Any, dict], dict],
    ) -> Any: ...

    def reserve_specialist(
        self,
        *,
        investigation_id: str,
        specialist_slug: str,
        ownership_token: str,
        lease_seconds: int = 900,
    ) -> dict: ...

    def promote_next_candidate(self, *, investigation_id: str) -> dict | None: ...

    def close_without_evidence(self, *, investigation_id: str) -> Any: ...

    def finalize_specialist(
        self,
        *,
        investigation_id: str,
        specialist_slug: str,
        ownership_token: str,
        merge: Callable[[Any, dict], tuple[str, dict]],
    ) -> Any: ...

    def persist_finalization(
        self,
        *,
        investigation_id: str,
        merge: Callable[[Any, dict], tuple[str, dict]],
    ) -> Any: ...

