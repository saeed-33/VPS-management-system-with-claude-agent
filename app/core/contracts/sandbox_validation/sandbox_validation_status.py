"""Contract class extracted from sandbox_validation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

class SandboxValidationStatus(StrEnum):
    """
    حالات اختبار الخطة من الانتظار حتى النجاح أو الفشل أو انتهاء الصلاحية.
    """
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    STALE = "stale"
