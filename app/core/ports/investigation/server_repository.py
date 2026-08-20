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

from .server_record import ServerRecord

class ServerRepositoryProtocol(Protocol):
    """
    يعرّف عملية جلب السيرفر لجمع الأدلة.
    """
    def get_by_id(self, server_id: int) -> ServerRecord | None:
        """
        يجلب سجل سيرفر حسب المعرف من أجل جمع الدليل.
        """
        ...
