from __future__ import annotations

from app.runtime.claude.native_monitoring import (
    ClaudeNativeMonitoringRunner,
    SERVER_SUPERVISOR_ALLOWED_TOOLS,
)


def test_c14_11_runtime_allows_mandatory_operational_tools():
    allowed = set(
        SERVER_SUPERVISOR_ALLOWED_TOOLS
    )

    assert "mcp__vps__run_monitoring" in allowed
    assert "mcp__vps__analyze_report" in allowed
    assert (
        "mcp__vps__get_available_specialists"
        in allowed
    )
    assert "mcp__vps__run_specialist" in allowed
    assert "Agent(specialist-worker)" in allowed


def test_c14_11_native_prompt_requires_real_mcp_execution():
    prompt = ClaudeNativeMonitoringRunner._prompt(
        server_id=2,
        job_id="acceptance-job",
    )

    assert (
        "mcp__vps__run_monitoring EXACTLY ONCE"
        in prompt
    )
    assert "mcp__vps__analyze_report" in prompt
    assert "Project tool results" in prompt
    assert "persisted records are authoritative" in prompt
    assert "Never use raw SSH" in prompt
    assert "should_investigate=true" in prompt
    assert "Agent(specialist-worker)" in prompt
    assert "investigation_id" in prompt
    assert "specialist_slug" in prompt
    assert "both required fields, description and prompt" in prompt
    assert "Do not stop after investigation creation" in prompt
