"""Request contract for collecting diagnostic evidence."""
from __future__ import annotations

from dataclasses import dataclass

from app.core.policies.diagnostic_policy.diagnostic_policy_result import (
    DiagnosticPolicyResult,
)


@dataclass(slots=True, frozen=True)
class EvidenceCollectionRequest:
    """Represents a diagnostic evidence request for one server."""

    evidence_id: str
    server_id: int
    policy_result: DiagnosticPolicyResult

    def __post_init__(self) -> None:
        """Validate request identity before execution."""
        if not self.evidence_id.strip():
            raise ValueError("evidence_id must not be empty.")
        if self.server_id < 1:
            raise ValueError("server_id must be >= 1.")
