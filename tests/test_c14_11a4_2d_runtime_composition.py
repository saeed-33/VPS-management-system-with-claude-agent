from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_runtime_composition_is_outside_builder():
    builder = (
        ROOT / "app/composition/builder.py"
    ).read_text(encoding="utf-8")
    runtime = (
        ROOT / "app/composition/runtime.py"
    ).read_text(encoding="utf-8")

    assert "build_runtime_composition(" in builder

    for constructor in (
        "MonitoringService(",
        "ProjectMcpToolBoundary(",
        "OllamaClaudeCommandBuilder(",
        "SubprocessClaudeSessionRunner(",
        "ClaudeRuntimeAdapter(",
        "ClaudeNativeMonitoringRunner(",
        "ClaudeSupervisor(",
        "MonitoringScheduler(",
    ):
        assert constructor not in builder
        assert constructor in runtime


def test_runtime_composition_keeps_ollama_claude_contract():
    runtime = (
        ROOT / "app/composition/runtime.py"
    ).read_text(encoding="utf-8")

    assert "claude_supervisor_runner = None" in runtime
    assert "base_url=settings.ollama_base_url" in runtime
    assert "settings.claude_runtime_executable" in runtime
    assert "settings.effective_claude_runtime_model" in runtime


def test_builder_is_composition_coordinator_after_a4_2d():
    builder = (
        ROOT / "app/composition/builder.py"
    ).read_text(encoding="utf-8")

    assert "build_repositories()" in builder
    assert "build_core_services(" in builder
    assert "build_retrieval_composition(" in builder
    assert "build_analysis_investigation_composition(" in builder
    assert "build_runtime_composition(" in builder
    assert "return ApplicationContainer(" in builder
