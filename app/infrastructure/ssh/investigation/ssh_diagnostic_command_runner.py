"""Class extracted from evidence_collection during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from datetime import UTC, datetime

from time import perf_counter

from typing import Protocol

from app.core.contracts.investigation.evidence_kind import EvidenceKind
from app.core.contracts.investigation.evidence_reference import EvidenceReference

from app.capabilities.investigation.source_location import extract_source_locations

from app.core.policies.diagnostic_policy.diagnostic_policy_result import DiagnosticPolicyResult

from asyncssh import Error

from app.infrastructure.ssh.client.client import SSHClient
from app.infrastructure.ssh.client.config import SSHConnectionConfig

from app.infrastructure.ssh.command_executor.executor import SSHCommandExecutor

from .diagnostic_execution_outcome import DiagnosticExecutionOutcome

class SSHDiagnosticCommandRunner:
    """
    ينفذ الأوامر التشخيصية عبر SSH.
    """
    async def run(
        self,
        *,
        config: SSHConnectionConfig,
        tool_id: str,
        command_text: str,
        timeout_seconds: float,
    ) -> DiagnosticExecutionOutcome:
        """
        يشغل أمرًا تشخيصيًا ويعيد المخرجات والحالة والمدة.
        """
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
