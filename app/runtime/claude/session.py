from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.runtime.claude.models import (
    ClaudeJobStatus,
)


@dataclass(slots=True)
class ClaudeSessionSnapshot:
    job_id: str
    status: ClaudeJobStatus = ClaudeJobStatus.QUEUED
    session_id: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None
    metadata: dict[str, object] = field(
        default_factory=dict
    )

    def mark_running(
        self,
        *,
        session_id: str | None = None,
    ) -> None:
        self.status = ClaudeJobStatus.RUNNING
        self.session_id = session_id
        self.started_at = datetime.now(
            timezone.utc
        )

    def mark_finished(
        self,
        *,
        status: ClaudeJobStatus,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> None:
        self.status = status
        self.error_code = error_code
        self.error_message = error_message
        self.completed_at = datetime.now(
            timezone.utc
        )
