from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
from pathlib import Path

import pytest
from app.core.contracts.servers import UpdateServerDTO


RUN_REAL_RUNTIME = (
    os.getenv(
        "AI_VPS_RUN_REAL_RUNTIME_TESTS",
        "",
    ).strip()
    == "1"
)

pytestmark = pytest.mark.skipif(
    not RUN_REAL_RUNTIME,
    reason=(
        "Real Claude/Ollama/MCP acceptance is opt-in. "
        "Set AI_VPS_RUN_REAL_RUNTIME_TESTS=1."
    ),
)


_WINDOWS_ABSOLUTE_PATH = re.compile(
    r"^(?P<drive>[A-Za-z]):[\\/](?P<rest>.+)$"
)


def _resolve_acceptance_runtime_path(value: str) -> str:
    raw = str(value).strip()
    direct = Path(raw)
    if direct.is_file():
        return str(direct)

    if os.getenv("WSL_DISTRO_NAME", "").strip():
        match = _WINDOWS_ABSOLUTE_PATH.match(raw)
        if match:
            translated = (
                Path("/mnt")
                / match.group("drive").lower()
                / match.group("rest").replace("\\", "/")
            )
            if translated.is_file():
                return str(translated)

    return raw


class _AcceptanceServerRepository:
    """Add only WSL path normalization around the real repository."""

    def __init__(self, delegate):
        self._delegate = delegate

    def get_by_id(self, server_id):
        server = self._delegate.get_by_id(server_id)
        if server is not None and server.private_key_path:
            server.private_key_path = _resolve_acceptance_runtime_path(
                server.private_key_path
            )
        return server

    def __getattr__(self, name):
        return getattr(self._delegate, name)


def _install_acceptance_ssh_path_normalization(container) -> None:
    repository = _AcceptanceServerRepository(
        container.server_repository
    )
    container.monitoring_service._server_repository = repository
    if container.evidence_collection_service is not None:
        container.evidence_collection_service._server_repository = repository


def _normalize_persisted_server_key_path(
    repository,
    *,
    server_id: int,
):
    server = repository.get_by_id(server_id)
    if server is None or not server.private_key_path:
        return lambda: None

    original = server.private_key_path
    normalized = _resolve_acceptance_runtime_path(original)
    if normalized == original:
        return lambda: None

    repository.update(
        server_id,
        UpdateServerDTO(private_key_path=normalized),
    )

    def restore() -> None:
        repository.update(
            server_id,
            UpdateServerDTO(private_key_path=original),
        )

    return restore



def _restore_operational_database_env(
    *,
    env_path: Path | None = None,
) -> None:
    # Real-runtime acceptance must use the application's operational DB.
    # Explicit process values are authoritative. The project .env is only a
    # fallback for values absent from the process environment. This function
    # runs before importing app.composition so cached settings see the final
    # effective environment.
    from dotenv import dotenv_values

    project_root = (
        Path(__file__).resolve().parents[2]
    )
    resolved_env_path = env_path or (project_root / ".env")

    if not resolved_env_path.is_file():
        pytest.fail(
            "Real-runtime acceptance requires the project .env file "
            f"for operational PostgreSQL settings: {resolved_env_path}"
        )

    values = dotenv_values(
        resolved_env_path
    )

    keys = (
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    )

    missing = [
        key
        for key in keys
        if not str(
            values.get(key) or ""
        ).strip()
    ]

    if missing:
        pytest.fail(
            "Project .env is missing operational PostgreSQL settings: "
            + ", ".join(missing)
        )

    for key in keys:
        if str(os.environ.get(key) or "").strip():
            continue
        os.environ[key] = str(values[key])

def _server_id() -> int:
    raw = os.getenv(
        "AI_VPS_REAL_RUNTIME_SERVER_ID",
        "",
    ).strip()

    if not raw:
        pytest.fail(
            "AI_VPS_REAL_RUNTIME_SERVER_ID is required "
            "for real-runtime acceptance."
        )

    try:
        value = int(raw)
    except ValueError:
        pytest.fail(
            "AI_VPS_REAL_RUNTIME_SERVER_ID must be an integer."
        )

    if value < 1:
        pytest.fail(
            "AI_VPS_REAL_RUNTIME_SERVER_ID must be >= 1."
        )

    return value


def test_c14_11_real_claude_ollama_mcp_cycle_persists_evidence(
    request: pytest.FixtureRequest,
):
    # Imports are intentionally inside the opt-in test so the normal
    # unit-test suite does not bootstrap the operational runtime.
    _restore_operational_database_env()

    try:
        from app.composition import container
    except Exception as exc:
        message = str(exc)

        if (
            "CLAUDE_RUNTIME_ENABLED requires LLM_ENABLED"
            in message
        ):
            pytest.fail(
                "Real-runtime acceptance configuration is invalid: "
                "CLAUDE_RUNTIME_ENABLED=true requires LLM_ENABLED=true. "
                "In PowerShell set: "
                '$env:LLM_ENABLED="true"; '
                '$env:LLM_PROVIDER="ollama"; '
                '$env:CLAUDE_RUNTIME_ENABLED="true"'
            )

        if (
            "CLAUDE_RUNTIME_ENABLED requires LLM_PROVIDER=ollama"
            in message
        ):
            pytest.fail(
                "Real-runtime acceptance requires "
                "LLM_PROVIDER=ollama. In PowerShell set: "
                '$env:LLM_PROVIDER="ollama"'
            )

        raise

    from app.runtime.claude.models import (
        ClaudeJobStatus,
    )
    from app.runtime.claude.observability import (
        ClaudeAgentObservabilityService,
    )
    from app.core.config import settings

    _install_acceptance_ssh_path_normalization(container)

    server_id = _server_id()
    request.addfinalizer(
        _normalize_persisted_server_key_path(
            container.server_repository,
            server_id=server_id,
        )
    )

    if not settings.claude_runtime_enabled:
        pytest.fail(
            "Claude runtime is disabled. "
            "Set CLAUDE_RUNTIME_ENABLED=true."
        )

    executable = (
        settings.claude_runtime_executable
    )

    if shutil.which(executable) is None:
        pytest.fail(
            "Claude executable was not found on PATH: "
            f"{executable}"
        )

    model = (
        settings.effective_claude_runtime_model
    ).strip()

    if not model:
        pytest.fail(
            "Claude/Ollama runtime model is empty."
        )

    server = (
        container.server_repository.get_by_id(
            server_id
        )
    )

    if server is None:
        pytest.fail(
            "Acceptance server does not exist: "
            f"server_id={server_id}"
        )

    previous_reports = (
        container.report_repository.list_reports(
            server_id=server_id,
            limit=1,
        )
    )

    previous_report_id = (
        previous_reports[0][0].id
        if previous_reports
        else None
    )

    result = asyncio.run(
        container.claude_supervisor.run(
            server_id
        )
    )

    assert (
        result.status
        == ClaudeJobStatus.COMPLETED
    )
    assert result.session_id

    tool_names = list(
        result.usage_metadata.get(
            "event_tool_names",
            [],
        )
    )

    required_tools = {
        "mcp__vps__run_monitoring",
        "mcp__vps__analyze_report",
    }

    assert required_tools.issubset(
        set(tool_names)
    )

    mcp_servers = list(
        result.usage_metadata.get(
            "event_mcp_servers",
            [],
        )
    )

    assert any(
        isinstance(item, dict)
        and item.get("name") == "vps"
        and item.get("status") == "connected"
        for item in mcp_servers
    )

    job = (
        container.agent_job_repository
        .get_by_job_id(
            result.job_id
        )
    )

    assert job is not None
    assert job.status == "completed"
    assert (
        job.claude_session_id
        == result.session_id
    )
    assert (
        job.turn_count
        == result.turn_count
    )
    assert (
        job.tool_call_count
        == result.tool_call_count
    )

    current_reports = (
        container.report_repository.list_reports(
            server_id=server_id,
            limit=1,
        )
    )

    assert current_reports

    report = current_reports[0][0]

    assert report.server_id == server_id

    if previous_report_id is not None:
        assert (
            report.id
            != previous_report_id
        )

    analysis = (
        container.analysis_repository
        .get_by_report_id(
            report.id
        )
    )

    assert analysis is not None
    assert analysis.server_id == server_id
    assert analysis.status == "completed"

    observability = (
        ClaudeAgentObservabilityService(
            container.agent_job_repository
        )
    )

    trace = observability.get_trace(
        result.job_id
    )

    assert trace is not None
    assert (
        trace["session_id"]
        == result.session_id
    )
    assert (
        trace["required_tools_verified"]
        is True
    )
    assert trace["mcp_connected"] is True

    investigations = (
        container.investigation_repository
        .list_by_report_id(
            report.id
        )
    )

    if (
        "mcp__vps__start_investigation"
        in tool_names
    ):
        assert investigations

    acceptance = {
        "status": "accepted",
        "server_id": server_id,
        "runtime_model": model,
        "job": {
            "job_id": result.job_id,
            "status": job.status,
            "session_id": (
                result.session_id
            ),
            "turn_count": (
                result.turn_count
            ),
            "tool_call_count": (
                result.tool_call_count
            ),
        },
        "report": {
            "report_id": report.id,
            "status": report.status,
        },
        "analysis": {
            "analysis_id": analysis.id,
            "status": analysis.status,
            "health_status": (
                analysis.health_status
            ),
            "analysis_source": (
                analysis.analysis_source
            ),
            "llm_called": (
                analysis.llm_called
            ),
        },
        "investigations": [
            {
                "investigation_id": (
                    item.investigation_id
                ),
                "status": item.status,
                "should_investigate": (
                    item.should_investigate
                ),
            }
            for item in investigations
        ],
        "tool_calls": tool_names,
        "mcp_servers": mcp_servers,
        "observability": {
            "duration_ms": (
                trace["duration_ms"]
            ),
            "required_tools_verified": (
                trace[
                    "required_tools_verified"
                ]
            ),
            "mcp_connected": (
                trace["mcp_connected"]
            ),
        },
    }

    print()
    print(
        "C.14.11 REAL RUNTIME ACCEPTANCE:"
    )
    print(
        json.dumps(
            acceptance,
            indent=2,
            default=str,
        )
    )
