"""
جزء من Remediation من التشخيص والاقتراح حتى sandbox/authorization والتنفيذ.

الموقع في المعمارية: Application capability / remediation.
يُستدعى بواسطة: Admin API أو MCP.
يعتمد مباشرة على: app.core.contracts.remediation، app.infrastructure.ssh.client، app.infrastructure.ssh.command_executor.
الحد المعماري: لا يسمح write operation بمجرد اقتراح LLM.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

import asyncio
import os
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from app.core.contracts.remediation import RemediationAction
from app.infrastructure.ssh.client import SSHClient, SSHConnectionConfig
from app.infrastructure.ssh.command_executor import SSHCommandExecutor


@dataclass(frozen=True, slots=True)
class WriteCommandResult:
    """
    يمثل WriteCommandResult مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    success: bool
    exit_status: int | None = None
    stdout: str = ""
    stderr: str = ""
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ServiceStateObservation:
    """
    يمثل ServiceStateObservation مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    state: str
    stdout: str = ""
    stderr: str = ""
    exit_status: int | None = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)


class ServiceStateEvidenceCollector(Protocol):
    """
    يمثل ServiceStateEvidenceCollector مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def collect(self, *, server_id: int, service: str) -> ServiceStateObservation:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى collect؛ المدخلات المهمة: server_id، service.
        تعيد ServiceStateObservation أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        ...


class WriteCommandRunner(Protocol):
    """
    يمثل WriteCommandRunner مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def run(self, *, server_id: int, action: RemediationAction, command: str, timeout_seconds: float) -> WriteCommandResult:
        """
        يشغّل workflow هذه الطبقة ويربط مراحله ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى run؛ المدخلات المهمة: server_id، action، command، timeout_seconds.
        تعيد WriteCommandResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        ...


class VerificationRunner(Protocol):
    """
    يمثل VerificationRunner مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def verify(self, *, server_id: int, action: RemediationAction) -> tuple[bool, dict]:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى verify؛ المدخلات المهمة: server_id، action.
        تعيد tuple[bool, dict] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        ...


class UnavailableWriteRunner:
    """
    يمثل UnavailableWriteRunner مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def run(self, **_kwargs) -> WriteCommandResult:
        """
        يشغّل workflow هذه الطبقة ويربط مراحله ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى run؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد WriteCommandResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return WriteCommandResult(success=False, error="safe_write_runner_not_configured")


class UnavailableVerificationRunner:
    """
    يمثل UnavailableVerificationRunner مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def verify(self, **_kwargs) -> tuple[bool, dict]:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى verify؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد tuple[bool, dict] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return False, {"error": "safe_verification_runner_not_configured"}


class UnavailableEvidenceCollector:
    """
    يمثل UnavailableEvidenceCollector مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def collect(self, **_kwargs) -> ServiceStateObservation:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى collect؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد ServiceStateObservation أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return ServiceStateObservation(
            state="unknown",
            error="safe_evidence_collector_not_configured",
        )



_WINDOWS_ABSOLUTE_PATH = re.compile(
    r"^(?P<drive>[A-Za-z]):[\\/](?P<rest>.+)$"
)


def _resolve_runtime_file_path(value: str) -> str:
    """
    Resolve a persisted runtime file path without changing its identity.

    A Windows absolute path stored in the shared database is translated to
    the equivalent /mnt/<drive>/... path when execution occurs under WSL.

    If no valid translation exists, return the original value so the SSH
    boundary fails closed with its normal FileNotFoundError.
    """
    raw = str(value).strip()

    direct = Path(raw)
    if direct.is_file():
        return str(direct)

    if os.getenv("WSL_DISTRO_NAME", "").strip():
        match = _WINDOWS_ABSOLUTE_PATH.match(raw)

        if match:
            drive = match.group("drive").lower()
            rest = match.group("rest").replace("\\", "/")

            translated = Path("/mnt") / drive / rest

            if translated.is_file():
                return str(translated)

    return raw


class _SSHNamedCommandRunner:
    """
    يمثل _SSHNamedCommandRunner مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, *, server_repository, private_key_path: str, known_hosts_path: str,
                 connect_timeout_seconds: float, command_timeout_seconds: float) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: server_repository، private_key_path، known_hosts_path، connect_timeout_seconds، command_timeout_seconds.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._server_repository = server_repository
        self._private_key_path = private_key_path
        self._known_hosts_path = known_hosts_path
        self._connect_timeout_seconds = connect_timeout_seconds
        self._command_timeout_seconds = command_timeout_seconds

    def _run_sync(self, coroutine_factory):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى _run_sync؛ المدخلات المهمة: coroutine_factory.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coroutine_factory())
        # MCP handlers are async but the domain service deliberately remains
        # synchronous for compatibility. Isolate the SSH event loop from the
        # caller's loop; the registered command is still the only command
        # supplied to this adapter.
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(lambda: asyncio.run(coroutine_factory())).result()

    async def _execute(self, *, server_id: int, command: str, command_name: str, timeout: float):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى _execute؛ المدخلات المهمة: server_id، command، command_name، timeout.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        server = self._server_repository.get_by_id(server_id)
        if server is None:
            return WriteCommandResult(success=False, error="server_not_found")
        config = SSHConnectionConfig(
            host=server.host,
            port=server.port,
            username=server.username,
            private_key_path=_resolve_runtime_file_path(
                server.private_key_path
                or self._private_key_path
            ),
            known_hosts_path=_resolve_runtime_file_path(
                self._known_hosts_path
            ),
            connect_timeout_seconds=self._connect_timeout_seconds,
        )
        try:
            async with SSHClient(config) as client:
                result = await SSHCommandExecutor(client).execute(
                    command_id=None,
                    command_name=command_name,
                    command_text=command,
                    execution_order=1,
                    timeout_seconds=min(timeout, self._command_timeout_seconds),
                    fingerprint_strategy="remediation_named_command",
                    fingerprint_config={"command_name": command_name},
                )
            return WriteCommandResult(
                success=result.success,
                exit_status=result.exit_status,
                stdout=result.stdout,
                stderr=result.stderr,
                error=result.error_message,
            )
        except Exception as exc:
            return WriteCommandResult(success=False, error=f"{type(exc).__name__}: {exc}")


class SSHNamedWriteRunner(_SSHNamedCommandRunner):
    """
    يمثل SSHNamedWriteRunner مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على _SSHNamedCommandRunner وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def run(self, *, server_id: int, action: RemediationAction, command: str, timeout_seconds: float) -> WriteCommandResult:
        """
        يشغّل workflow هذه الطبقة ويربط مراحله ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى run؛ المدخلات المهمة: server_id، action، command، timeout_seconds.
        تعيد WriteCommandResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._run_sync(lambda: self._execute(
            server_id=server_id, command=command, command_name=action.action_type, timeout=timeout_seconds
        ))


class SSHServiceVerifier(_SSHNamedCommandRunner):
    """
    يمثل SSHServiceVerifier مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على _SSHNamedCommandRunner وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def verify(self, *, server_id: int, action: RemediationAction) -> tuple[bool, dict]:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى verify؛ المدخلات المهمة: server_id، action.
        تعيد tuple[bool, dict] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self.verify_state(
            server_id=server_id,
            service=action.target,
            expected_state="active",
        )

    def verify_state(self, *, server_id: int, service: str, expected_state: str) -> tuple[bool, dict]:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى verify_state؛ المدخلات المهمة: server_id، service، expected_state.
        تعيد tuple[bool, dict] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        # The target was validated by the write registry before reaching this
        # adapter. The read command is fixed and does not accept shell text.
        result = self._run_sync(lambda: self._execute(
            server_id=server_id,
            command=f"systemctl is-active {service}",
            command_name="verify_service_state",
            timeout=30.0,
        ))
        observed = result.stdout.strip()
        return observed == expected_state, {
            "expected": expected_state,
            "observed": observed,
            "exit_status": result.exit_status,
            "error": result.error,
        }


class SSHServiceStateEvidenceCollector(_SSHNamedCommandRunner):
    """
    يمثل SSHServiceStateEvidenceCollector مسؤولية محددة داخل طبقة Application capability / remediation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Admin API أو MCP
    ويعتمد على _SSHNamedCommandRunner وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def collect(self, *, server_id: int, service: str) -> ServiceStateObservation:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى collect؛ المدخلات المهمة: server_id، service.
        تعيد ServiceStateObservation أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        # Evidence collection accepts only the validated service name supplied
        # by the registered remediation tool. It never accepts shell text.
        result = self._run_sync(lambda: self._execute(
            server_id=server_id,
            command=f"systemctl is-active {service}",
            command_name="collect_remediation_service_state",
            timeout=30.0,
        ))
        state = result.stdout.strip()
        if state not in {"active", "inactive", "failed", "activating", "deactivating"}:
            state = "unknown"
        return ServiceStateObservation(
            state=state,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_status=result.exit_status,
            error=result.error,
            metadata={"command_name": "collect_remediation_service_state"},
        )
