"""قرار مسار إعادة استخدام التحليل."""
from __future__ import annotations

from enum import StrEnum


class AnalysisDecision(StrEnum):
    """المسار الذي اختارته سياسة إعادة استخدام التحليل."""

    FULL = "full"
    REUSE = "reuse"
    ASSISTED = "assisted"
