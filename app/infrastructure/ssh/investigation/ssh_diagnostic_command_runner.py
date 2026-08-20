"""SSH adapter for executing approved diagnostic commands."""
from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter

from asyncssh import Error as SSHError

from app.core.contracts.investigation.diagnostic_connection_config import (
    DiagnosticConnectionConfig,
)
from app.core.contracts.investigation.diagnostic_execution_outcome import (
    DiagnosticExecutionOutcome,
)
from app.infrastructure.ssh.client.client import SSHClient
from app.infrastructure.ssh.client.config import SSHConnectionConfig
from app.infrastructure.ssh.command_executor.executor import SSHCommandExecutor


class SSHDiagnosticCommandRunner:
    """Executes bounded diagnostic commands over SSH."""

    async def run(
        self,
        *,
        config: DiagnosticConnectionConfig,
        tool_id: str,
        command_text: str,
        timeout_seconds: float,
    ) -> DiagnosticExecutionOutcome:
        """Execute one command and normalize transport failures."""
        started_at = datetime.now(UTC)
        started_counter = perf_counter()
        ssh_config = SSHConnectionConfig(
            host=config.host,
            port=config.port,
            username=config.username,
            private_key_path=config.private_key_path,
            known_hosts_path=config.known_hosts_path,
            connect_timeout_seconds=config.connect_timeout_seconds,
        )

        try:
            async with SSHClient(ssh_config) as ssh_client:
                result = await SSHCommandExecutor(ssh_client).execute(
                    command_id=None,
                    command_name=f"diagnostic:{tool_id}",
                    command_text=command_text,
                    execution_order=1,
                    timeout_seconds=timeout_seconds,
                    fingerprint_strategy="diagnostic_tool",
                    fingerprint_config={"tool_id": tool_id},
                )
            return DiagnosticExecutionOutcome(
                success=result.success,
                exit_status=result.exit_status,
                stdout=result.stdout,
                stderr=result.stderr,
                error_message=result.error_message,
                started_at=result.started_at,
                finished_at=result.finished_at,
                duration_ms=result.duration_ms,
            )
        except (SSHError, OSError, TimeoutError, FileNotFoundError) as exc:
            return DiagnosticExecutionOutcome(
                success=False,
                exit_status=None,
                stdout="",
                stderr="",
                error_message=f"{type(exc).__name__}: {exc}",
                started_at=started_at,
                finished_at=datetime.now(UTC),
                duration_ms=round((perf_counter() - started_counter) * 1000, 2),
            )
