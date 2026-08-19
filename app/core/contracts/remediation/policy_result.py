"""Contract class extracted from remediation.py during the structure refactor."""

from __future__ import annotations

import hashlib

import json

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

from .policy_decision import PolicyDecision

@dataclass(slots=True, frozen=True)
class PolicyResult:
    """
    نتيجة تقييم السياسة مع قرارها والأسباب التي يمكن مراجعتها.
    """
    decision: PolicyDecision
    reasons: tuple[str, ...]

    @property
    def allowed(self) -> bool:
        """يحدد هل القرار يسمح بالمتابعة دون اعتبار وجود موافقة إضافية."""
        return self.decision == PolicyDecision.ALLOW
