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
class EvidenceCollectionRequest:
    """
    يمثل طلب جمع أدلة مرتبطًا بسيرفر ومجموعة أوامر.
    """
    evidence_id: str
    server_id: int
    policy_result: DiagnosticPolicyResult

    def __post_init__(self) -> None:
        """
        يتحقق من صحة بيانات EvidenceCollectionRequest قبل استخدامها في التحقيق.
        """
        if not self.evidence_id.strip():
            raise ValueError("evidence_id must not be empty.")
        if self.server_id < 1:
            raise ValueError("server_id must be >= 1.")
