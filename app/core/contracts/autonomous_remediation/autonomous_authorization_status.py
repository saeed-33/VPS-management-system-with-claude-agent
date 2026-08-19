"""Contract class extracted from autonomous_remediation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

class AutonomousAuthorizationStatus(StrEnum):
    """
    حالة التفويض الذي يربط قرار السياسة بخطة تغيير محددة.
    """
    VALID = "valid"
    CONSUMED = "consumed"
    STALE = "stale"
    EXPIRED = "expired"
    REVOKED = "revoked"
