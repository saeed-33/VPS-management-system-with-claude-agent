"""
تنفيذ فحص مراقبة واحد عبر اتصال SSH وإرجاع نتيجته المقاسة.
"""
import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter

import asyncssh

from app.infrastructure.ssh.client.client import SSHClient
from .result import CommandExecutionResult


@dataclass(slots=True)
class SSHCommandExecutor:
    """
    منفذ ينفذ فحصًا واحدًا بمهلة محددة ويحول كل فشل إلى نتيجة قابلة للتقرير.
    """

    def __init__(
        self,
        ssh_client: SSHClient,
    ) -> None:
        """
        يهيئ عميل التكامل ويحفظ إعدادات الاتصال اللازمة للمرحلة التي يستخدمه فيها.
        """
        self._ssh_client = ssh_client

    async def execute(
        self,
        *,
        command_id: int | None,
        command_name: str,
        command_text: str,
        execution_order: int,
        timeout_seconds: float,
        fingerprint_strategy: str,
        fingerprint_config: dict,
    ) -> CommandExecutionResult:
        """
        ينفذ نص فحص مسجل عبر SSH، يطبق المهلة، ويحفظ stdout وstderr وحالة الخروج والمدة.
        """
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
                fingerprint_strategy=fingerprint_strategy,
                fingerprint_config=fingerprint_config,
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
                fingerprint_strategy=fingerprint_strategy,
                fingerprint_config=fingerprint_config,
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
                fingerprint_strategy=fingerprint_strategy,
                fingerprint_config=fingerprint_config,
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
                fingerprint_strategy=fingerprint_strategy,
                fingerprint_config=fingerprint_config,
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
        """
        يحسب مدة فحص SSH بالميلي ثانية لتسجيلها في التقرير.
        """
        return round(
            (perf_counter() - started_counter) * 1000,
            2,
        )
