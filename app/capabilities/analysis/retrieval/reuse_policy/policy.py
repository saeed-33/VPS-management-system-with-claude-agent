"""سياسة اختيار مسار التحليل."""
from __future__ import annotations

from .decision import AnalysisDecision
from .decision_result import AnalysisDecisionResult

class AnalysisReusePolicy:
    """
    يطبق قواعد اختيار مسار التحليل بناءً على البصمة والسياق التاريخي وخيار الإجبار.
    """

    def decide(
        self,
        *,
        fingerprint_match: bool,
        historical_context_available: bool,
        assisted_enabled: bool,
        force: bool = False,
    ) -> AnalysisDecisionResult:
        """
        يختار التحليل الكامل عند الإجبار، وإعادة الاستخدام عند تطابق البصمة، والمساعدة عند توفر سياق تاريخي صالح.
        """
        if force:
            return AnalysisDecisionResult(
                decision=AnalysisDecision.FULL,
                reason="forced_analysis",
            )

        if fingerprint_match:
            return AnalysisDecisionResult(
                decision=AnalysisDecision.REUSE,
                reason="exact_fingerprint_match",
            )

        if assisted_enabled and historical_context_available:
            return AnalysisDecisionResult(
                decision=AnalysisDecision.ASSISTED,
                reason="historical_context_available",
            )

        return AnalysisDecisionResult(
            decision=AnalysisDecision.FULL,
            reason="no_usable_historical_context",
        )
