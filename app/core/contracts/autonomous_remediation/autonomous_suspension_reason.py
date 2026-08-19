"""Contract class extracted from autonomous_remediation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

class AutonomousSuspensionReason(StrEnum):
    """
    سبب إيقاف المعالجة الذاتية بعد فشل أو مخالفة سلامة أو قرار مشغل.
    """
    EXECUTION_FAILURE = "execution_failure"
    VERIFICATION_FAILURE = "verification_failure"
    ROLLBACK_FAILURE = "rollback_failure"
    CONSECUTIVE_FAILURE_THRESHOLD = "consecutive_failure_threshold"
    OPERATOR_SUSPENSION = "operator_suspension"
    SAFETY_VIOLATION = "safety_violation"
