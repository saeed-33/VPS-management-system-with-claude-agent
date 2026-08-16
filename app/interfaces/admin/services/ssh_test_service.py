"""
اختبار اتصال SSH من واجهة الإدارة.

تحمل الخدمة إعدادات السيرفر ومفتاحه، تنفذ أمرًا بسيطًا للتحقق من الاتصال،
وتعيد نتيجة آمنة قابلة للعرض بدل تسريب استثناءات العميل.
"""
from dataclasses import dataclass

from app.infrastructure.ssh.client import (
    SSHClient,
    SSHConnectionConfig,
)
from app.infrastructure.ssh.command_executor import (
    SSHCommandExecutor,
)
from app.infrastructure.database.repositories.server_repository import (
    ServerRepository,
)
from app.core.exceptions import ServerNotFoundError


@dataclass(slots=True, frozen=True)
class SSHTestResult:
    """
    يمثل نتيجة اختبار SSH مع الرسالة واسم المضيف عند توفره.
    """
    success: bool
    message: str
    hostname: str | None = None


class SSHTestService:
    """
    ينفذ اختبار اتصال SSH لسيرفر محفوظ ويعيد نتيجة إدارية منظمة.
    """
    def __init__(
        self,
        *,
        server_repository: ServerRepository,
        default_private_key_path: str,
        known_hosts_path: str,
        connect_timeout_seconds: float,
        command_timeout_seconds: float,
    ) -> None:
        """
        يحفظ مستودع السيرفر وإعدادات مفاتيح SSH ومسارات known_hosts والمهل الزمنية.
        """
        self._server_repository = server_repository
        self._default_private_key_path = (
            default_private_key_path
        )
        self._known_hosts_path = known_hosts_path
        self._connect_timeout_seconds = (
            connect_timeout_seconds
        )
        self._command_timeout_seconds = (
            command_timeout_seconds
        )

    async def test(
        self,
        server_id: int,
    ) -> SSHTestResult:
        """
        يجلب السيرفر، ينشئ إعداد اتصال SSH، ينفذ فحصًا بسيطًا، ويعيد نجاح الاتصال أو رسالة آمنة.
        """
        server = self._server_repository.get_by_id(
            server_id
        )

        if server is None:
            raise ServerNotFoundError(server_id)

        private_key_path = (
            server.private_key_path
            or self._default_private_key_path
        )

        config = SSHConnectionConfig(
            host=server.host,
            port=server.port,
            username=server.username,
            private_key_path=private_key_path,
            known_hosts_path=self._known_hosts_path,
            connect_timeout_seconds=(
                self._connect_timeout_seconds
            ),
        )

        try:
            async with SSHClient(config) as client:
                executor = SSHCommandExecutor(client)

                result = await executor.execute(
                    command_id=None,
                    command_name="SSH connection test",
                    command_text="hostname",
                    execution_order=1,
                    timeout_seconds=(
                        self._command_timeout_seconds
                    ),
                    fingerprint_strategy="ssh_connection_test",
                    fingerprint_config={
                        "command_name": "hostname",
                        "purpose": "admin_ssh_connectivity_test",
                    },
                )

            if not result.success:
                return SSHTestResult(
                    success=False,
                    message=(
                        result.error_message
                        or result.stderr
                        or "SSH test failed."
                    ),
                )

            return SSHTestResult(
                success=True,
                message="SSH connection succeeded.",
                hostname=result.stdout.strip(),
            )

        except Exception as exc:
            return SSHTestResult(
                success=False,
                message=(
                    f"{type(exc).__name__}: {exc}"
                ),
            )
