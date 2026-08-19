"""Contract class extracted from investigation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

@dataclass(slots=True, frozen=True)
class InvestigationBudget:
    """
    حدود تمنع التحقيق من تجاوز عدد المتخصصين أو الجولات أو الأفعال المسموحة.
    """
    max_specialists: int = 4
    max_rounds: int = 3
    max_actions: int = 12

    def __post_init__(self) -> None:
        """يتحقق من أن حدود التحقيق موجبة أو غير سالبة حسب طبيعة كل حد."""
        if self.max_specialists < 1:
            raise ValueError(
                "max_specialists must be >= 1."
            )
        if self.max_rounds < 1:
            raise ValueError(
                "max_rounds must be >= 1."
            )
        if self.max_actions < 0:
            raise ValueError(
                "max_actions must be >= 0."
            )
