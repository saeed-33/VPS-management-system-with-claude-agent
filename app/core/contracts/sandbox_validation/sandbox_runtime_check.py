"""Contract class extracted from sandbox_validation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

@dataclass(frozen=True, slots=True)
class SandboxRuntimeCheck:
    """
    نتيجة فحص توفر بيئة الاختبار قبل تشغيل الخطة فيها.
    """
    available: bool
    runtime: str
    reason: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)
