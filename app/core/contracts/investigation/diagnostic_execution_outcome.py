"""Result contract for executing one diagnostic command."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class DiagnosticExecutionOutcome:
    """Represents diagnostic command output and execution status."""

    success: bool
    exit_status: int | None
    stdout: str
    stderr: str
    error_message: str | None
    started_at: datetime
    finished_at: datetime
    duration_ms: float
