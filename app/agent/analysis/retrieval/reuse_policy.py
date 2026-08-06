from dataclasses import dataclass
from enum import StrEnum


class AnalysisDecision(StrEnum):
    REUSE = "reuse"
    ASSISTED = "assisted"
    FULL = "full"


@dataclass(slots=True, frozen=True)
class AnalysisDecisionResult:
    decision: AnalysisDecision
    reason: str


class AnalysisReusePolicy:
    """
    Central policy for selecting the report analysis path.

    Direct reuse remains restricted to exact fingerprint matches.
    Semantic or vector similarity may provide assisted context only.
    """

    def decide(
        self,
        *,
        fingerprint_match: bool,
        historical_context_available: bool,
        assisted_enabled: bool,
        force: bool = False,
    ) -> AnalysisDecisionResult:
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
