"""Contract class extracted from investigation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

class SpecialistTaskStatus(StrEnum):
    """
    حالات مهمة المتخصص أثناء طلب الفحص وتحليل نتيجته.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
