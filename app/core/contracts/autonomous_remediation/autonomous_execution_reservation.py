"""Contract class extracted from autonomous_remediation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

@dataclass(slots=True, frozen=True)
class AutonomousExecutionReservation:
    """
    حجز يمنع تنفيذ خطة المعالجة الذاتية نفسها بالتوازي أو التكرار.
    """
    reservation_id: str
    idempotency_key: str
    status: str
    policy_id: str
    plan_id: str
    authorization_id: str | None = None
    execution_id: str | None = None
    owner_token: str | None = None
