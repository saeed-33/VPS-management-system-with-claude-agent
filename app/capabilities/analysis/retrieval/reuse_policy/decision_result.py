"""نتيجة قرار إعادة استخدام التحليل."""
from __future__ import annotations

from dataclasses import dataclass

from .decision import AnalysisDecision

@dataclass(slots=True, frozen=True)
class AnalysisDecisionResult:
    """
    يحمل قرار السياسة وسبب اختياره لتسجيله وتتبع أثره.
    """
    decision: AnalysisDecision
    reason: str
