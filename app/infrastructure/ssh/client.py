"""
إدارة اتصال SSH موثق إلى سيرفر مراقب.

يتحقق العميل من مفتاح الاتصال وknown_hosts، ويفتح الاتصال عند الحاجة ويغلقه
بشكل مضمون حتى تستخدم دورة المراقبة قناة آمنة ومحدودة.
"""
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType

import asyncssh


@dataclass(slots=True, frozen=True)
class SSHConnectionConfig:
    """
    إعدادات اتصال SSH تشمل هوية السيرفر ومفاتيح التحقق والمهلة.
    """
    host: str
    port: int
    username: str

    private_key_path: str
    known_hosts_path: str

    connect_timeout_seconds: float = 15.0


class SSHClient:
    """
    عميل يفتح اتصال SSH موثقًا ويغلقه ليستخدمه منفذ فحوص المراقبة.
    """

    def __init__(
        self,
        config: SSHConnectionConfig,
    ) -> None:
        """
        يهيئ عميل التكامل ويحفظ إعدادات الاتصال اللازمة للمرحلة التي يستخدمه فيها.
        """
        self._config = config
        self._connection: (
            asyncssh.SSHClientConnection | None
        ) = None

    @property
    def connection(
        self,
    ) -> asyncssh.SSHClientConnection:
        """
        يعيد اتصال SSH المفتوح أو يرفض الاستخدام قبل اكتمال الاتصال.
        """
        if self._connection is None:
            raise RuntimeError(
                "SSH connection is not open."
            )

        return self._connection

    @property
    def is_connected(self) -> bool:
        """
        يحدد هل يملك العميل اتصال SSH صالحًا حاليًا.
        """
        return self._connection is not None

    async def connect(self) -> None:
        """
        يفتح اتصال SSH بعد التحقق من المفتاح وknown_hosts وإعدادات السيرفر.
        """
        if self._connection is not None:
            return

        private_key_path = Path(
            self._config.private_key_path
        )

        known_hosts_path = Path(
            self._config.known_hosts_path
        )

        if not private_key_path.is_file():
            raise FileNotFoundError(
                f"SSH private key does not exist: "
                f"{private_key_path}"
            )

        if not known_hosts_path.is_file():
            raise FileNotFoundError(
                f"SSH known_hosts file does not exist: "
                f"{known_hosts_path}"
            )

        self._connection = await asyncssh.connect(
            host=self._config.host,
            port=self._config.port,
            username=self._config.username,
            client_keys=[str(private_key_path)],
            known_hosts=str(known_hosts_path),
            connect_timeout=(
                self._config.connect_timeout_seconds
            ),
        )

    async def close(self) -> None:
        """
        يغلق اتصال SSH وينتظر انتهاءه حتى لا تبقى جلسة بعيدة معلقة.
        """
        if self._connection is None:
            return

        self._connection.close()
        await self._connection.wait_closed()

        self._connection = None

    async def __aenter__(self) -> "SSHClient":
        """
        يفتح الاتصال عند دخول سياق async ويعيد العميل الجاهز للاستخدام.
        """
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        يغلق الاتصال عند الخروج من سياق async سواء انتهت الدورة بنجاح أو بفشل.
        """
        await self.close()