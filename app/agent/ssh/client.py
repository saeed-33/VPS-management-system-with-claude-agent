from dataclasses import dataclass
from pathlib import Path
from types import TracebackType

import asyncssh


@dataclass(slots=True, frozen=True)
class SSHConnectionConfig:
    host: str
    port: int
    username: str

    private_key_path: str
    known_hosts_path: str

    connect_timeout_seconds: float = 15.0


class SSHClient:
    """
    مسؤول عن دورة حياة اتصال SSH واحد.

    لا ينفذ منطق المراقبة ولا يحفظ النتائج في قاعدة البيانات.
    """

    def __init__(
        self,
        config: SSHConnectionConfig,
    ) -> None:
        self._config = config
        self._connection: (
            asyncssh.SSHClientConnection | None
        ) = None

    @property
    def connection(
        self,
    ) -> asyncssh.SSHClientConnection:
        if self._connection is None:
            raise RuntimeError(
                "SSH connection is not open."
            )

        return self._connection

    @property
    def is_connected(self) -> bool:
        return self._connection is not None

    async def connect(self) -> None:
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
        if self._connection is None:
            return

        self._connection.close()
        await self._connection.wait_closed()

        self._connection = None

    async def __aenter__(self) -> "SSHClient":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()