"""Port for executing the enabled monitoring commands."""
from __future__ import annotations

from typing import Protocol

from app.core.contracts.monitoring.monitoring_connection_config import (
    MonitoringConnectionConfig,
)
from app.core.contracts.reports.command_execution_data import CommandExecutionData
from app.core.ports.monitoring.monitoring_command_record import MonitoringCommandRecord


class MonitoringCommandRunnerPort(Protocol):
    """Executes bounded monitoring commands through an external adapter."""

    async def run(
        self,
        *,
        config: MonitoringConnectionConfig,
        commands: list[MonitoringCommandRecord],
    ) -> list[CommandExecutionData]: ...

