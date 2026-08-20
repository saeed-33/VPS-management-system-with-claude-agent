"""Port for executing an approved diagnostic command."""
from __future__ import annotations

from typing import Protocol

from app.core.contracts.investigation.diagnostic_connection_config import (
    DiagnosticConnectionConfig,
)
from app.core.contracts.investigation.diagnostic_execution_outcome import (
    DiagnosticExecutionOutcome,
)


class DiagnosticCommandRunnerPort(Protocol):
    """Executes one bounded diagnostic command."""

    async def run(
        self,
        *,
        config: DiagnosticConnectionConfig,
        tool_id: str,
        command_text: str,
        timeout_seconds: float,
    ) -> DiagnosticExecutionOutcome: ...
