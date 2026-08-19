"""Contract class extracted from autonomous_remediation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

class AutonomousPolicyStatus(StrEnum):
    """
    حالات سياسة المعالجة الذاتية من التفعيل حتى التعليق الوقائي.
    """
    ENABLED = "enabled"
    DISABLED = "disabled"
    SUSPENDED = "suspended"
