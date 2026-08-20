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

class DiagnosticCommandRunner(Protocol):
    """
    يعرّف عقد تشغيل أمر تشخيصي على سيرفر.
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
        ...
