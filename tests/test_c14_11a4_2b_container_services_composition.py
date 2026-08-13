from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]


def test_application_container_is_outside_builder():
    builder = (
        ROOT / "app/composition/builder.py"
    ).read_text(encoding="utf-8")
    container = (
        ROOT / "app/composition/container.py"
    ).read_text(encoding="utf-8")

    assert "class ApplicationContainer" not in builder
    assert "class ApplicationContainer" in container
    assert (
        "from app.composition.container import ApplicationContainer"
        in builder
    )


def test_core_service_construction_is_outside_builder():
    builder = (
        ROOT / "app/composition/builder.py"
    ).read_text(encoding="utf-8")
    services = (
        ROOT / "app/composition/services.py"
    ).read_text(encoding="utf-8")

    assert "services = build_core_services(" in builder
    assert "class CoreServiceBundle" in services
    assert "def build_core_services(" in services

    constructor_names = {
        "ServerService",
        "CommandService",
        "MonitoringProfileService",
        "ReportQueryService",
        "SpecialistDefinitionService",
        "SpecialistRegistry",
        "InvestigationRouter",
        "InvestigationPersistenceService",
        "InvestigationReadService",
        "InvestigationRuntimeSnapshotService",
        "KnowledgeSourceService",
        "KnowledgeSourceRegistry",
        "KnowledgeIngestionService",
        "KnowledgeChunkingService",
        "DiagnosticPolicyEngine",
        "EvidenceCollectionService",
        "ClaudeAgentJobService",
        "RemediationService",
    }

    builder_tree = ast.parse(builder)
    services_tree = ast.parse(services)

    builder_calls = {
        node.func.id
        for node in ast.walk(builder_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
    }
    service_calls = {
        node.func.id
        for node in ast.walk(services_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
    }

    for name in constructor_names:
        assert name not in builder_calls
        assert name in service_calls


def test_analysis_and_runtime_are_outside_builder():
    builder = (
        ROOT / "app/composition/builder.py"
    ).read_text(encoding="utf-8")
    analysis = (
        ROOT / "app/composition/analysis.py"
    ).read_text(encoding="utf-8")
    runtime = (
        ROOT / "app/composition/runtime.py"
    ).read_text(encoding="utf-8")

    assert "AnalysisOrchestrator(" not in builder
    assert "SpecialistInvestigationLoop(" not in builder
    assert "ClaudeNativeMonitoringRunner(" not in builder

    assert "AnalysisOrchestrator(" in analysis
    assert "SpecialistInvestigationLoop(" in analysis
    assert "ClaudeNativeMonitoringRunner(" in runtime


