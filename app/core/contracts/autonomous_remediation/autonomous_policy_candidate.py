"""Contract class extracted from autonomous_remediation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

@dataclass(slots=True, frozen=True)
class AutonomousPolicyCandidate:
    """
    مرشح سياسة مع إحصاءات التاريخ التي استخدمت في التقييم.
    """
    issue_fingerprint: str
    action_type: str
    target: str
    execution_count: int
    verified_success_count: int
    failure_count: int
    rollback_failure_count: int
    success_rate: float
    reason_codes: tuple[str, ...]
