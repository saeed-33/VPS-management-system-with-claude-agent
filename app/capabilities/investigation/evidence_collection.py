from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter
from typing import Protocol

from app.core.contracts.investigation import EvidenceKind, EvidenceReference
from app.core.policies.diagnostic_policy import DiagnosticPolicyResult
from app.infrastructure.ssh import SSHError
from app.infrastructure.ssh.client import SSHClient, SSHConnectionConfig
from app.infrastructure.ssh.command_executor import SSHCommandExecutor


@dataclass(slots=True, frozen=True)
class DiagnosticExecutionOutcome:
    success: bool
    exit_status: int | None
    stdout: str
    stderr: str
    error_message: str | None
    started_at: datetime
    finished_at: datetime
    duration_ms: float


class DiagnosticCommandRunner(Protocol):
    async def run(
        self,
        *,
        config: SSHConnectionConfig,
        tool_id: str,
        command_text: str,
        timeout_seconds: float,
    ) -> DiagnosticExecutionOutcome:
        ...


class ServerRecord(Protocol):
    id: int
    host: str
    port: int
    username: str
    private_key_path: str | None


class ServerRepositoryProtocol(Protocol):
    def get_by_id(self, server_id: int) -> ServerRecord | None:
        ...


@dataclass(slots=True, frozen=True)
class EvidenceCollectionRequest:
    evidence_id: str
    server_id: int
    policy_result: DiagnosticPolicyResult

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError("evidence_id must not be empty.")
        if self.server_id < 1:
            raise ValueError("server_id must be >= 1.")


class SSHDiagnosticCommandRunner:
    async def run(
        self,
        *,
        config: SSHConnectionConfig,
        tool_id: str,
        command_text: str,
        timeout_seconds: float,
    ) -> DiagnosticExecutionOutcome:
        started_at = datetime.now(UTC)
        started_counter = perf_counter()

        try:
            async with SSHClient(config) as ssh_client:
                result = await SSHCommandExecutor(ssh_client).execute(
                    command_id=None,
                    command_name=f"diagnostic:{tool_id}",
                    command_text=command_text,
                    execution_order=1,
                    timeout_seconds=timeout_seconds,
                    fingerprint_strategy="diagnostic_tool",
                    fingerprint_config={"tool_id": tool_id},
                )

            return DiagnosticExecutionOutcome(
                success=result.success,
                exit_status=result.exit_status,
                stdout=result.stdout,
                stderr=result.stderr,
                error_message=result.error_message,
                started_at=result.started_at,
                finished_at=result.finished_at,
                duration_ms=result.duration_ms,
            )

        except (
            SSHError,
            OSError,
            TimeoutError,
            FileNotFoundError,
        ) as exc:
            return DiagnosticExecutionOutcome(
                success=False,
                exit_status=None,
                stdout="",
                stderr="",
                error_message=f"{type(exc).__name__}: {exc}",
                started_at=started_at,
                finished_at=datetime.now(UTC),
                duration_ms=round(
                    (perf_counter() - started_counter) * 1000,
                    2,
                ),
            )


class EvidenceCollectionService:
    def __init__(
        self,
        *,
        server_repository: ServerRepositoryProtocol,
        default_private_key_path: str,
        known_hosts_path: str,
        connection_timeout_seconds: float,
        runner: DiagnosticCommandRunner | None = None,
    ) -> None:
        if not default_private_key_path.strip():
            raise ValueError(
                "default_private_key_path must not be empty."
            )
        if not known_hosts_path.strip():
            raise ValueError("known_hosts_path must not be empty.")
        if connection_timeout_seconds <= 0:
            raise ValueError(
                "connection_timeout_seconds must be > 0."
            )

        self._server_repository = server_repository
        self._default_private_key_path = default_private_key_path
        self._known_hosts_path = known_hosts_path
        self._connection_timeout_seconds = connection_timeout_seconds
        self._runner = runner or SSHDiagnosticCommandRunner()

    async def collect(
        self,
        request: EvidenceCollectionRequest,
    ) -> EvidenceReference:
        policy = request.policy_result

        if not policy.allowed:
            raise PermissionError(
                "Diagnostic evidence collection requires an ALLOW policy result."
            )

        command_text = policy.rendered_command
        timeout_seconds = policy.timeout_seconds
        output_limit_chars = policy.output_limit_chars

        if (
            not command_text
            or timeout_seconds is None
            or output_limit_chars is None
        ):
            raise ValueError(
                "Approved diagnostic policy result has an incomplete execution envelope."
            )

        server = self._server_repository.get_by_id(
            request.server_id
        )

        if server is None:
            raise ValueError(
                f"Server with id {request.server_id} was not found."
            )

        config = SSHConnectionConfig(
            host=server.host,
            port=server.port,
            username=server.username,
            private_key_path=(
                server.private_key_path
                or self._default_private_key_path
            ),
            known_hosts_path=self._known_hosts_path,
            connect_timeout_seconds=(
                self._connection_timeout_seconds
            ),
        )

        outcome = await self._runner.run(
            config=config,
            tool_id=policy.tool_id,
            command_text=command_text,
            timeout_seconds=timeout_seconds,
        )

        excerpt, truncated = self._render_excerpt(
            outcome=outcome,
            limit=output_limit_chars,
        )

        return EvidenceReference(
            evidence_id=request.evidence_id,
            kind=EvidenceKind.COMMAND_RESULT,
            title=(
                f"Diagnostic tool {policy.tool_id} "
                f"on server {request.server_id}"
            ),
            source_id=request.server_id,
            excerpt=excerpt,
            metadata={
                "server_id": request.server_id,
                "specialist_slug": policy.specialist_slug,
                "tool_id": policy.tool_id,
                "command_text": command_text,
                "success": outcome.success,
                "exit_status": outcome.exit_status,
                "error_message": outcome.error_message,
                "started_at": outcome.started_at.isoformat(),
                "finished_at": outcome.finished_at.isoformat(),
                "duration_ms": outcome.duration_ms,
                "timeout_seconds": timeout_seconds,
                "output_limit_chars": output_limit_chars,
                "stdout_chars": len(outcome.stdout),
                "stderr_chars": len(outcome.stderr),
                "excerpt_truncated": truncated,
                "risk": policy.metadata.get("risk"),
                "requires_sudo": policy.metadata.get(
                    "requires_sudo"
                ),
            },
        )

    @staticmethod
    def _render_excerpt(
        *,
        outcome: DiagnosticExecutionOutcome,
        limit: int,
    ) -> tuple[str, bool]:
        parts: list[str] = []

        if outcome.stdout:
            parts.append("STDOUT:\n" + outcome.stdout)

        if outcome.stderr:
            parts.append("STDERR:\n" + outcome.stderr)

        if outcome.error_message:
            parts.append("ERROR:\n" + outcome.error_message)

        if not parts:
            parts.append("(command produced no output)")

        text = "\n\n".join(parts)

        if len(text) <= limit:
            return text, False

        suffix = "\n...[truncated]"

        if limit <= len(suffix):
            return text[:limit], True

        return text[: limit - len(suffix)] + suffix, True
