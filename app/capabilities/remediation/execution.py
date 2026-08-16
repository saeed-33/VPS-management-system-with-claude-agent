"""
عقود ومنفذات أوامر المعالجة والتحقق.

يعرّف الملف نتائج الكتابة وملاحظات حالة الخدمة، ومنفذات SSH والمنفذات غير
المتاحة، وجامعي الأدلة الذين يستخدمونها خدمة المعالجة للتحقق الآمن.
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
    يمثل نتيجة تنفيذ أمر كتابة مع الخروج والمخرجات والمدة ورسالة الخطأ.
    """
    success: bool
    exit_status: int | None = None
    stdout: str = ""
    stderr: str = ""
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ServiceStateObservation:
    """
    يمثل الدليل المقروء عن حالة خدمة قبل أو بعد تنفيذ المعالجة.
    """
    state: str
    stdout: str = ""
    stderr: str = ""
    exit_status: int | None = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)


class ServiceStateEvidenceCollector(Protocol):
    """
    يعرّف عقد جمع دليل حالة خدمة من السيرفر المستهدف.
    """
    def collect(self, *, server_id: int, service: str) -> ServiceStateObservation:
        """
        يعرّف عملية جمع دليل حالة الخدمة من المنفذ المرتبط بالسيرفر.
        """
        ...


class WriteCommandRunner(Protocol):
    """
    يعرّف عقد تشغيل أمر تغيير على السيرفر.
    """
    def run(self, *, server_id: int, action: RemediationAction, command: str, timeout_seconds: float) -> WriteCommandResult:
        """
        يعرّف عملية تشغيل أمر كتابة على السيرفر المستهدف.
        """
        ...


class VerificationRunner(Protocol):
    """
    يعرّف عقد التحقق من أثر التغيير بعد التنفيذ.
    """
    def verify(self, *, server_id: int, action: RemediationAction) -> tuple[bool, dict]:
        """
        يعرّف عملية التحقق من أثر التغيير بعد تشغيله.
        """
        ...


class UnavailableWriteRunner:
    """
    يمثل منفذ كتابة غير متاح ويعيد فشلًا صريحًا بدل تنفيذ وهمي.
    """
    def run(self, **_kwargs) -> WriteCommandResult:
        """
        يعيد نتيجة فشل توضّح أن تنفيذ الكتابة غير متاح.
        """
        return WriteCommandResult(success=False, error="safe_write_runner_not_configured")


class UnavailableVerificationRunner:
    """
    يمثل متحققًا غير متاح ويبلغ عن عدم إمكانية التحقق.
    """
    def verify(self, **_kwargs) -> tuple[bool, dict]:
        """
        يعيد نتيجة فشل توضّح أن التحقق غير متاح.
        """
        return False, {"error": "safe_verification_runner_not_configured"}


class UnavailableEvidenceCollector:
    """
    يمثل جامع أدلة غير متاح ويعيد نتيجة عدم توفر الدليل.
    """
    def collect(self, **_kwargs) -> ServiceStateObservation:
        """
        يعيد دليلًا يوضح أن جمع حالة الخدمة غير متاح.
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
    يحل مسار ملف runtime المسموح باستخدامه في تنفيذ المعالجة.
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
    يوفر أساسًا مشتركًا لتشغيل أمر مسمى عبر جلسة SSH.
    """
    def __init__(self, *, server_repository, private_key_path: str, known_hosts_path: str,
                 connect_timeout_seconds: float, command_timeout_seconds: float) -> None:
        """
        يهيئ اتصال SSH واسم الأمر وخيارات المهلة والتنفيذ.
        """
        self._server_repository = server_repository
        self._private_key_path = private_key_path
        self._known_hosts_path = known_hosts_path
        self._connect_timeout_seconds = connect_timeout_seconds
        self._command_timeout_seconds = command_timeout_seconds

    def _run_sync(self, coroutine_factory):
        """
        ينفذ استدعاء SSH المتزامن داخل واجهة المنفذ.
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coroutine_factory())
        # تصل الطلبات من مسار غير متزامن، لكن يبقى التنفيذ هنا متوافقًا مع
        # الخدمة الحالية. لا يسمح هذا المسار إلا بالأمر المسجل مسبقًا.
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(lambda: asyncio.run(coroutine_factory())).result()

    async def _execute(self, *, server_id: int, command: str, command_name: str, timeout: float):
        """
        يشغل الأمر عبر SSH ويحوّل الخرج والاستثناءات إلى نتيجة قابلة للتدقيق.
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
    ينفذ أمر كتابة مسمى عبر SSH ويحوّل النتيجة إلى عقد نتيجة الكتابة.
    """
    def run(self, *, server_id: int, action: RemediationAction, command: str, timeout_seconds: float) -> WriteCommandResult:
        """
        ينفذ أمر الكتابة المسمى عبر SSH ويعيد مخرجاته ومدة تشغيله.
        """
        return self._run_sync(lambda: self._execute(
            server_id=server_id, command=command, command_name=action.action_type, timeout=timeout_seconds
        ))


class SSHServiceVerifier(_SSHNamedCommandRunner):
    """
    يتحقق عبر SSH من أثر تغيير خدمة، بما في ذلك حالتها المتوقعة.
    """
    def verify(self, *, server_id: int, action: RemediationAction) -> tuple[bool, dict]:
        """
        ينفذ فحص الخدمة عبر SSH ويعيد نتيجة التحقق من أثر التغيير.
        """
        return self.verify_state(
            server_id=server_id,
            service=action.target,
            expected_state="active",
        )

    def verify_state(self, *, server_id: int, service: str, expected_state: str) -> tuple[bool, dict]:
        """
        يقرأ حالة الخدمة عبر SSH ويقارنها بالحالة المتوقعة.
        """
        # وصل الهدف بعد اجتياز قائمة التغيير المسموح بها؛ وفحص القراءة ثابت
        # ولا يقبل نص أوامر من خارج السجل.
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
    يجمع حالة خدمة وأدلتها عبر SSH من السيرفر المستهدف.
    """
    def collect(self, *, server_id: int, service: str) -> ServiceStateObservation:
        """
        يجمع ملاحظة حالة الخدمة ومخرجاتها عبر SSH لتوثيق الدليل.
        """
        # يجمع الدليل باسم خدمة تم التحقق منه عبر أداة المعالجة المسجلة، ولا
        # يحول إدخال المستخدم إلى نص أوامر قابل للتنفيذ.
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
