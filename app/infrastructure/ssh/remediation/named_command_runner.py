"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.infrastructure.ssh.client.client import SSHClient
from app.infrastructure.ssh.client.config import SSHConnectionConfig
from app.infrastructure.ssh.command_executor.executor import SSHCommandExecutor

from .runtime_path import _resolve_runtime_file_path
from app.core.contracts.remediation.write_command_result import WriteCommandResult

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
