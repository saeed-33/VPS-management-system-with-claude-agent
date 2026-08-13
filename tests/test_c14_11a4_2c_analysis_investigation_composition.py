from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_analysis_and_investigation_composition_is_outside_builder():
    builder = (
        ROOT / "app/composition/builder.py"
    ).read_text(encoding="utf-8")
    analysis = (
        ROOT / "app/composition/analysis.py"
    ).read_text(encoding="utf-8")

    assert "build_retrieval_composition(" in builder
    assert "build_analysis_investigation_composition(" in builder

    assert "AnalysisOrchestrator(" not in builder
    assert "SpecialistInvestigationLoop(" not in builder
    assert "KnowledgeHybridRetriever(" not in builder
    assert "HybridRetriever(" not in builder

    assert "AnalysisOrchestrator(" in analysis
    assert "SpecialistInvestigationLoop(" in analysis
    assert "KnowledgeHybridRetriever(" in analysis
    assert "HybridRetriever(" in analysis


def test_claude_mcp_and_scheduler_wiring_moves_to_runtime_composition():
    builder = (
        ROOT / "app/composition/builder.py"
    ).read_text(encoding="utf-8")
    runtime = (
        ROOT / "app/composition/runtime.py"
    ).read_text(encoding="utf-8")

    for constructor in (
        "ProjectMcpToolBoundary(",
        "ClaudeNativeMonitoringRunner(",
        "MonitoringScheduler(",
    ):
        assert constructor not in builder
        assert constructor in runtime

