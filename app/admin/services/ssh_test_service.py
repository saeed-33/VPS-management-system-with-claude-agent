from dataclasses import dataclass

from app.agent.ssh.client import (
    SSHClient,
    SSHConnectionConfig,
)
from app.agent.ssh.command_executor import (
    SSHCommandExecutor,
)
from app.shared.database.repositories.server_repository import (
    ServerRepository,
)
from app.shared.exceptions import ServerNotFoundError


@dataclass(slots=True, frozen=True)
class SSHTestResult:
    success: bool
    message: str
    hostname: str | None = None


class SSHTestService:
    def __init__(
        self,
        *,
        server_repository: ServerRepository,
        default_private_key_path: str,
        known_hosts_path: str,
        connect_timeout_seconds: float,
        command_timeout_seconds: float,
    ) -> None:
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