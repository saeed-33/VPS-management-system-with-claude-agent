from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RemediationRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RemediationPlanStatus(StrEnum):
    PROPOSED = "proposed"
    SANDBOX_PASSED = "sandbox_passed"
    SANDBOX_FAILED = "sandbox_failed"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    BLOCKED = "blocked"


class SandboxResultStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"


@dataclass(slots=True, frozen=True)
class CreateRemediationPlanDTO:
    plan_id: str
    investigation_id: str
    title: str
    problem_summary: str
    proposed_actions: list[dict[str, Any]]
    diagnosis_claim_ids: list[str]
    evidence_ids: list[str]
    risk_level: str = RemediationRisk.MEDIUM.value
    rollback_plan: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.plan_id.strip():
            raise ValueError(
                "plan_id must not be empty."
            )
        if not self.investigation_id.strip():
            raise ValueError(
                "investigation_id must not be empty."
            )
        if not self.title.strip():
            raise ValueError(
                "title must not be empty."
            )
        if not self.problem_summary.strip():
            raise ValueError(
                "problem_summary must not be empty."
            )
        if not self.proposed_actions:
            raise ValueError(
                "proposed_actions must not be empty."
            )
        if not self.diagnosis_claim_ids:
            raise ValueError(
                "diagnosis_claim_ids must not be empty."
            )
        if not self.evidence_ids:
            raise ValueError(
                "evidence_ids must not be empty."
            )
        if self.risk_level not in {
            item.value for item in RemediationRisk
        }:
            raise ValueError(
                "risk_level is invalid."
            )


@dataclass(slots=True, frozen=True)
class CreateSandboxResultDTO:
    result_id: str
    plan_id: str
    status: str
    before_evidence_ids: list[str]
    after_evidence_ids: list[str]
    logs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.result_id.strip():
            raise ValueError(
                "result_id must not be empty."
            )
        if not self.plan_id.strip():
            raise ValueError(
                "plan_id must not be empty."
            )
        if self.status not in {
            item.value for item in SandboxResultStatus
        }:
            raise ValueError(
                "sandbox status is invalid."
            )
