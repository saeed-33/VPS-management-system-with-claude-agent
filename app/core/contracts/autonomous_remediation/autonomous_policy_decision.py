"""Contract class extracted from autonomous_remediation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

from .autonomous_decision_outcome import AutonomousDecisionOutcome

@dataclass(slots=True, frozen=True)
class AutonomousPolicyDecision:
    """
    سجل قرار سياسة قابل للمراجعة يشرح مآل المعالجة الذاتية وأسبابه.
    """
    decision_id: str
    outcome: AutonomousDecisionOutcome
    reason_codes: tuple[str, ...]
    human_readable_reasons: tuple[str, ...]
    policy_id: str | None = None
    policy_version: int | None = None
    plan_id: str | None = None
    plan_fingerprint: str | None = None
    issue_fingerprint: str | None = None
    server_id: int | None = None
    action_type: str | None = None
    target: str | None = None
    evaluated_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
