from __future__ import annotations

import asyncio
import json
from pathlib import Path

from app.interfaces.mcp.registry import ProjectMcpToolBoundary
from app.interfaces.mcp.schemas import ProjectToolCall
from app.runtime.claude.result_parser import ClaudeStructuredResultParser
from app.runtime.claude.exceptions import ClaudeStructuredOutputError
from tools.acceptance.evaluation.contracts import EvaluationMetric
from tools.acceptance.evaluation.safety_runtime import (
    evaluate_policy_cases,
    evaluate_provider_cases,
)


ROOT = Path(__file__).resolve().parents[1]


def _boundary() -> ProjectMcpToolBoundary:
    return ProjectMcpToolBoundary(
        server_service=None,
        monitoring_profile_service=None,
        monitoring_service=None,
        report_query_service=None,
    )


def test_c14_12_startup_recovers_interrupted_jobs():
    text = (ROOT / "app/main.py").read_text(encoding="utf-8")

    assert "recover_interrupted_jobs" in text
    assert "Recovered %s interrupted Claude agent job(s)." in text


def test_c14_12_mcp_surface_is_bounded_and_stable():
    boundary = _boundary()
    definitions = boundary.list_tools()

    assert len(definitions) == 25
    expected_bounded_write_ids = {
        "apply_approved_remediation",
        "create_remediation_plan",
        "request_user_approval",
        "run_specialist",
        "start_investigation",
            "test_remediation_in_sandbox",
            "attempt_autonomous_remediation",
        }
    assert {
        item.tool_id
        for item in definitions
        if not item.read_only
    } == expected_bounded_write_ids

    forbidden = (
        "raw_ssh",
        "raw_sql",
        "execute_command",
        "database_query",
        "psql",
        "shell",
        "arbitrary filesystem",
        "unbounded subprocess",
    )
    serialized = json.dumps(
        [
            {
                "tool_id": item.tool_id,
                "description": item.description,
                "input_schema": item.input_schema,
            }
            for item in definitions
        ],
        sort_keys=True,
    ).lower()

    assert all(term not in serialized for term in forbidden)


def test_c14_12_unknown_and_unregistered_tools_fail_closed():
    async def run() -> None:
        for tool_id in (
            "raw_ssh",
            "raw_sql",
            "execute_command",
            "database_query",
        ):
            result = await _boundary().execute(
                ProjectToolCall(tool_id=tool_id, arguments={})
            )
            assert result.success is False
            assert result.error_code == "unknown_tool"

    asyncio.run(run())


def test_c14_12_claude_malformed_output_fails_closed():
    parser = ClaudeStructuredResultParser()

    try:
        parser.parse("not-json")
    except ClaudeStructuredOutputError:
        pass
    else:
        raise AssertionError("Malformed Claude output was accepted.")


def test_c14_12_controlled_policy_and_provider_failures_are_measured():
    policy = evaluate_policy_cases()
    provider = asyncio.run(evaluate_provider_cases())

    assert len(policy) == 10
    assert len(provider) == 10
    assert all(item.passed for item in policy)
    assert all(item.passed for item in provider)
    assert {item.metric for item in policy} == {
        EvaluationMetric.POLICY_SAFETY
    }
    assert {item.metric for item in provider} == {
        EvaluationMetric.PROVIDER_RESILIENCE
    }
