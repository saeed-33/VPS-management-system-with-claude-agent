import asyncio

from app.agent.evaluation.contracts import (
    EvaluationMetric,
)
from app.agent.evaluation.safety_runtime import (
    evaluate_policy_cases,
    evaluate_provider_cases,
    evaluate_routing_cases,
)


def test_routing_runtime_emits_ten_passes():
    items = evaluate_routing_cases()

    assert len(items) == 10
    assert all(
        item.metric
        == EvaluationMetric.ROUTING_RECALL
        for item in items
    )
    assert all(
        item.passed
        for item in items
    )


def test_policy_runtime_emits_ten_passes():
    items = evaluate_policy_cases()

    assert len(items) == 10
    assert all(
        item.metric
        == EvaluationMetric.POLICY_SAFETY
        for item in items
    )
    assert all(
        item.passed
        for item in items
    )


def test_provider_runtime_emits_ten_safe_results():
    items = asyncio.run(
        evaluate_provider_cases()
    )

    assert len(items) == 10
    assert all(
        item.metric
        == EvaluationMetric.PROVIDER_RESILIENCE
        for item in items
    )
    assert all(
        item.passed
        for item in items
    )
