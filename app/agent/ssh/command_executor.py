import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter

import asyncssh

from app.agent.ssh.client import SSHClient


@dataclass(slots=True)
class CommandExecutionResult:
    command_id: int | None
    command_name: str
    command_text: str
    execution_order: int

    success: bool
    exit_status: int | None

    stdout: str
    stderr: str
    error_message: str | None

    started_at: datetime
    finished_at: datetime
    duration_ms: float


class SSHCommandExecutor:
    """
    ينفذ أوامر Linux عبر اتصال SSH مفتوح مسبقًا.
    """

    def __init__(
        self,
        ssh_client: SSHClient,
    ) -> None:
        self._ssh_client = ssh_client

    async def execute(
        self,
        *,
        command_id: int | None,
        command_name: str,
        command_text: str,
        execution_order: int,
        timeout_seconds: float,
    ) -> CommandExecutionResult:
        started_at = datetime.now(UTC)
        started_counter = perf_counter()

        try:
            result = await asyncio.wait_for(
                self._ssh_client.connection.run(
                    command_text,
                    check=False,
                ),
                timeout=timeout_seconds,
            )

            finished_at = datetime.now(UTC)
            duration_ms = self._duration_ms(
                started_counter
            )

            exit_status = result.exit_status
            success = exit_status == 0

            return CommandExecutionResult(
                command_id=command_id,
                command_name=command_name,
                command_text=command_text,
                execution_order=execution_order,
                success=success,
                exit_status=exit_status,
                stdout=result.stdout.strip(),
                stderr=result.stderr.strip(),
                error_message=(
                    None
                    if success
                    else (
                        "Command returned a non-zero "
                        "exit status."
                    )
                ),
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
            )

        except TimeoutError:
            return CommandExecutionResult(
                command_id=command_id,
                command_name=command_name,
                command_text=command_text,
                execution_order=execution_order,
                success=False,
                exit_status=None,
                stdout="",
                stderr="",
                error_message=(
                    f"Command timed out after "
                    f"{timeout_seconds} seconds."
                ),
                started_at=started_at,
                finished_at=datetime.now(UTC),
                duration_ms=self._duration_ms(
                    started_counter
                ),
            )

        except (
            asyncssh.Error,
            OSError,
        ) as exc:
            return CommandExecutionResult(
                command_id=command_id,
                command_name=command_name,
                command_text=command_text,
                execution_order=execution_order,
                success=False,
                exit_status=None,
                stdout="",
                stderr="",
                error_message=(
                    f"{type(exc).__name__}: {exc}"
                ),
                started_at=started_at,
                finished_at=datetime.now(UTC),
                duration_ms=self._duration_ms(
                    started_counter
                ),
            )

        except Exception as exc:
            return CommandExecutionResult(
                command_id=command_id,
                command_name=command_name,
                command_text=command_text,
                execution_order=execution_order,
                success=False,
                exit_status=None,
                stdout="",
                stderr="",
                error_message=(
                    f"Unexpected command error: "
                    f"{type(exc).__name__}: {exc}"
                ),
                started_at=started_at,
                finished_at=datetime.now(UTC),
                duration_ms=self._duration_ms(
                    started_counter
                ),
            )

    @staticmethod
    def _duration_ms(
        started_counter: float,
    ) -> float:
        return round(
            (perf_counter() - started_counter) * 1000,
            2,
        )