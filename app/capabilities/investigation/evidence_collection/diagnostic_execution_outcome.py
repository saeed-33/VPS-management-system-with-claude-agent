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

@dataclass(slots=True, frozen=True)
class DiagnosticExecutionOutcome:
    """
    يمثل نتيجة تشغيل أمر تشخيصي ومخرجاته وحالته.
    """
    success: bool
    exit_status: int | None
    stdout: str
    stderr: str
    error_message: str | None
    started_at: datetime
    finished_at: datetime
    duration_ms: float
