import pytest

from app.capabilities.analysis.retrieval.reuse_policy import (
    AnalysisDecision,
    AnalysisReusePolicy,
)


@pytest.fixture
def policy() -> AnalysisReusePolicy:
    return AnalysisReusePolicy()


def test_exact_fingerprint_reuses_analysis(policy):
    result = policy.decide(
        fingerprint_match=True,
        historical_context_available=False,
        assisted_enabled=True,
    )

    assert result.decision == AnalysisDecision.REUSE
    assert result.reason == "exact_fingerprint_match"


def test_force_always_requires_full_analysis(policy):
    result = policy.decide(
        fingerprint_match=True,
        historical_context_available=True,
        assisted_enabled=True,
        force=True,
    )

    assert result.decision == AnalysisDecision.FULL
    assert result.reason == "forced_analysis"


def test_compatible_historical_context_is_assisted(policy):
    result = policy.decide(
        fingerprint_match=False,
        historical_context_available=True,
        assisted_enabled=True,
    )

    assert result.decision == AnalysisDecision.ASSISTED


def test_context_is_ignored_when_assisted_is_disabled(policy):
    result = policy.decide(
        fingerprint_match=False,
        historical_context_available=True,
        assisted_enabled=False,
    )

    assert result.decision == AnalysisDecision.FULL


def test_no_context_requires_full_analysis(policy):
    result = policy.decide(
        fingerprint_match=False,
        historical_context_available=False,
        assisted_enabled=True,
    )

    assert result.decision == AnalysisDecision.FULL
