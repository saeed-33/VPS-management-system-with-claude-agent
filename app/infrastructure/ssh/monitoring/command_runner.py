"""SSH adapter for executing the enabled monitoring commands."""
from __future__ import annotations

from app.core.contracts.monitoring.monitoring_connection_config import (
    MonitoringConnectionConfig,
)
from app.core.contracts.reports.command_execution_data import CommandExecutionData
from app.core.ports.monitoring.monitoring_command_record import MonitoringCommandRecord
from app.infrastructure.ssh.client.client import SSHClient
from app.infrastructure.ssh.client.config import SSHConnectionConfig
from app.infrastructure.ssh.command_executor.executor import SSHCommandExecutor


class SSHMonitoringCommandRunner:
    """Runs bounded monitoring commands through the SSH infrastructure."""

    async def run(
        self,
        *,
        config: MonitoringConnectionConfig,
        commands: list[MonitoringCommandRecord],
    ) -> list[CommandExecutionData]:
        """Execute commands in order and translate results to a core contract."""
        ssh_config = SSHConnectionConfig(
            host=config.host,
            port=config.port,
            username=config.username,
            private_key_path=config.private_key_path,
            known_hosts_path=config.known_hosts_path,
            connect_timeout_seconds=config.connect_timeout_seconds,
        )

        executions: list[CommandExecutionData] = []
        async with SSHClient(ssh_config) as ssh_client:
            executor = SSHCommandExecutor(ssh_client)
            for command in sorted(commands, key=lambda item: item.execution_order):
                result = await executor.execute(
                    command_id=command.id,
                    command_name=command.name,
                    command_text=command.command,
                    execution_order=command.execution_order,
                    timeout_seconds=command.timeout_seconds,
                    fingerprint_strategy=getattr(command, "fingerprint_strategy", "monitoring_command"),
                    fingerprint_config=getattr(command, "fingerprint_config", {}),
                )
                executions.append(
                    CommandExecutionData(
                        command_id=result.command_id,
                        command_name=result.command_name,
                        command_text=result.command_text,
                        execution_order=result.execution_order,
                        success=result.success,
                        exit_status=result.exit_status,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        error_message=result.error_message,
                        started_at=result.started_at,
                        finished_at=result.finished_at,
                        duration_ms=result.duration_ms,
                        fingerprint_strategy=result.fingerprint_strategy,
                        fingerprint_config=result.fingerprint_config,
                    )
                )
        return executions

