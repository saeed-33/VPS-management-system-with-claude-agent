"""
Adapter لاتصال SSH وتنفيذ أوامر Linux مع timeouts ونتائج منظمة.

الموقع في المعمارية: External execution infrastructure.
يُستدعى بواسطة: Monitoring أو خدمات اختبار الاتصال.
يعتمد مباشرة على: app.infrastructure.ssh.client.
الحد المعماري: لا يختار profile ولا يقرر remediation.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter

import asyncssh

from app.infrastructure.ssh.client import SSHClient


@dataclass(slots=True)
class CommandExecutionResult:
    """
    يمثل CommandExecutionResult مسؤولية محددة داخل طبقة External execution infrastructure.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Monitoring أو خدمات اختبار الاتصال
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    command_id: int | None
    command_name: str
    command_text: str
    execution_order: int

    success: bool
    exit_status: int | None

    stdout: str
    stderr: str
    error_message: str | None

    fingerprint_strategy: str
    fingerprint_config: dict

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
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة External execution infrastructure.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: ssh_client.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يشغّل workflow هذه الطبقة ويربط مراحله ضمن طبقة External execution infrastructure.

        تُستدعى عندما يصل workflow إلى execute؛ المدخلات المهمة: command_id، command_name، command_text، execution_order، timeout_seconds، fingerprint_strategy.
        تعيد CommandExecutionResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة External execution infrastructure.

        تُستدعى عندما يصل workflow إلى _duration_ms؛ المدخلات المهمة: started_counter.
        تعيد float أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return round(
            (perf_counter() - started_counter) * 1000,
            2,
        )
