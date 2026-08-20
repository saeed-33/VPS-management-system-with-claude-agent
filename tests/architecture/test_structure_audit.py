"""Tests for application structure and package layout rules."""

from __future__ import annotations

import ast
from pathlib import Path

from tools.dev.generate_project_structure import ROOT, should_skip
from tools.dev.structure_audit import audit, top_level_class_names


def test_top_level_class_names_excludes_nested_classes() -> None:
    tree = ast.parse(
        """
class Owner:
    class Nested:
        pass

class Other:
    pass
"""
    )

    assert top_level_class_names(tree) == ["Owner", "Other"]


def test_audit_reports_multiple_top_level_classes(tmp_path) -> None:
    source = tmp_path / "mixed.py"
    source.write_text("class First:\n    pass\n\nclass Second:\n    pass\n", encoding="utf-8")

    violations = audit(tmp_path, max_lines=None)

    assert violations == [
        {
            "kind": "multiple_top_level_classes",
            "path": "mixed.py",
            "count": 2,
            "classes": ("First", "Second"),
        }
    ]


def test_audit_reports_large_files(tmp_path) -> None:
    source = tmp_path / "large.py"
    source.write_text("pass\n" * 4, encoding="utf-8")

    violations = audit(tmp_path, max_lines=3)

    assert violations == [
        {
            "kind": "file_too_large",
            "path": "large.py",
            "lines": 4,
            "limit": 3,
        }
    ]


def test_current_application_sources_are_parseable() -> None:
    violations = audit(Path("app"), max_lines=None)

    assert [item for item in violations if item["kind"] == "syntax_error"] == []


def test_current_application_sources_meet_the_structure_gate() -> None:
    assert audit(Path("app"), max_lines=350) == []


def test_generated_structure_ignores_local_only_output_directories() -> None:
    for relative_path in (
        ".claude/runtime-events/session.json",
        ".tmp/github-logs/output.txt",
        "draft/.codex-test-venv/Lib/site-packages/example.py",
        "docs/report/rendered_final/page-1.png",
    ):
        assert should_skip(ROOT / relative_path) is True


def test_app_keeps_init_files_only_at_main_package_boundaries() -> None:
    expected = {
        Path("app/__init__.py"),
        Path("app/capabilities/__init__.py"),
        Path("app/composition/__init__.py"),
        Path("app/core/__init__.py"),
        Path("app/core/ports/__init__.py"),
        Path("app/infrastructure/__init__.py"),
        Path("app/interfaces/__init__.py"),
        Path("app/runtime/__init__.py"),
        Path("app/runtime/claude/__init__.py"),
    }

    actual = set(Path("app").rglob("__init__.py"))

    assert actual == expected


def test_package_exports_are_explicit_at_public_boundaries() -> None:
    marker_packages = {
        Path("app/__init__.py"),
        Path("app/capabilities/__init__.py"),
        Path("app/core/__init__.py"),
        Path("app/core/ports/__init__.py"),
        Path("app/infrastructure/__init__.py"),
        Path("app/interfaces/__init__.py"),
        Path("app/runtime/__init__.py"),
    }
    for path in marker_packages:
        assert "__all__: list[str] = []" in path.read_text(encoding="utf-8")

    composition = Path("app/composition/__init__.py").read_text(encoding="utf-8")
    runtime = Path("app/runtime/claude/__init__.py").read_text(encoding="utf-8")
    assert '"build_container"' in composition
    assert '"container"' in composition
    assert '__all__ = ["ClaudeNativeMonitoringRunner"]' in runtime


def test_core_contracts_meet_the_current_structure_gate() -> None:
    assert audit(Path("app/core/contracts"), max_lines=350) == []


def test_capabilities_do_not_keep_ambiguous_generic_module_names() -> None:
    """تمنع أسماء الوحدات العامة التي تخفي مسؤولية الملف."""
    forbidden_names = {
        "service.py",
        "constants.py",
        "factories.py",
        "support.py",
        "helpers.py",
        "utils.py",
        "common.py",
        "models.py",
        "context.py",
    }
    offenders = [
        path.relative_to(Path("app"))
        for path in Path("app/capabilities").rglob("*.py")
        if path.name in forbidden_names
    ]
    assert offenders == []


def test_core_contracts_are_grouped_into_subpackages() -> None:
    root = Path("app/core/contracts")
    expected = {
        "agent_jobs",
        "analysis",
        "autonomous_remediation",
        "commands",
        "final_diagnosis",
        "investigation",
        "investigation_read_models",
        "investigations",
        "knowledge_sources",
        "profiles",
        "remediation",
        "remediation_events",
        "reports",
        "sandbox_validation",
        "servers",
        "source_location",
        "specialist_reasoning",
        "specialists",
    }

    assert {path.name for path in root.iterdir() if path.is_dir()} >= expected
    assert {
        path.name
        for path in root.glob("*.py")
        if path.name != "__init__.py"
    } == set()


def test_core_exceptions_and_multi_class_policies_are_grouped() -> None:
    root = Path("app/core")
    policy_root = root / "policies"
    expected_packages = {
        root / "exceptions",
        policy_root / "diagnostic_policy",
        policy_root / "diagnostic_tools",
        policy_root / "remediation_tools",
    }

    assert all(path.is_dir() for path in expected_packages)
    assert not (root / "exceptions.py").exists()
    assert not (policy_root / "diagnostic_policy.py").exists()
    assert not (policy_root / "diagnostic_tools.py").exists()
    assert not (policy_root / "remediation_tools.py").exists()
    assert all(audit(path, max_lines=350) == [] for path in expected_packages)


def test_investigation_multi_class_modules_are_grouped() -> None:
    root = Path("app/capabilities/investigation")
    expected_packages = {
        "correlation",
        "evidence_collection",
        "execution_contracts",
        "final_diagnosis_synthesizer",
        "investigation_router",
        "runtime_snapshot_service",
        "specialist_context",
        "specialist_execution_service",
        "specialist_investigation_loop",
        "specialist_reasoning_agent",
        "specialist_registry",
    }

    assert {path.name for path in root.iterdir() if path.is_dir()} >= expected_packages
    assert {
        path.name
        for path in root.glob("*.py")
        if path.name != "__init__.py"
    } == {
        "backlog_worker.py",
        "persistence_service.py",
        "read_service.py",
        "source_location.py",
        "specialist_service.py",
    }
    assert [
        item
        for item in audit(root, max_lines=None)
        if item["kind"] == "multiple_top_level_classes"
    ] == []


def test_analysis_full_text_retriever_is_grouped() -> None:
    root = Path("app/capabilities/analysis/retrieval")
    package = root / "full_text_retriever"

    assert package.is_dir()
    assert not (root / "full_text_retriever.py").exists()
    assert audit(package, max_lines=350) == []


def test_analysis_retrieval_components_are_grouped() -> None:
    root = Path("app/capabilities/analysis/retrieval")
    expected = {
        "hybrid_retriever",
        "reuse_policy",
        "structured_compatibility",
    }

    assert {path.name for path in root.iterdir() if path.is_dir()} >= expected
    assert not (root / "hybrid_retriever.py").exists()
    assert not (root / "reuse_policy.py").exists()
    assert not (root / "structured_compatibility.py").exists()
    assert all(audit(root / name, max_lines=350) == [] for name in expected)


def test_analysis_orchestrator_is_grouped() -> None:
    root = Path("app/capabilities/analysis")
    package = root / "analysis_orchestrator"

    assert package.is_dir()
    assert not (root / "analysis_orchestrator.py").exists()
    assert audit(package, max_lines=350) == []


def test_knowledge_components_are_grouped() -> None:
    root = Path("app/capabilities/knowledge")
    expected = {
        "chunker",
        "indexer",
        "ingestion_contracts",
        "parsers",
        "retrieval",
        "source_loader",
        "source_registry",
    }

    assert {path.name for path in root.iterdir() if path.is_dir()} >= expected
    for name in expected:
        assert audit(root / name, max_lines=350) == []
    assert {
        path.name
        for path in root.glob("*.py")
        if path.name != "__init__.py"
    } == {
        "chunking_service.py",
        "ingestion_service.py",
        "source_service.py",
    }


def test_monitoring_components_are_grouped() -> None:
    root = Path("app/capabilities/monitoring")
    expected = {"scheduler", "service"}

    assert {path.name for path in root.iterdir() if path.is_dir()} >= expected
    assert not (root / "scheduler.py").exists()
    assert not (root / "service.py").exists()
    assert all(audit(root / name, max_lines=350) == [] for name in expected)


def test_remediation_components_are_grouped() -> None:
    root = Path("app/capabilities/remediation")
    expected = {"execution", "autonomous_execution_service", "service"}

    assert {path.name for path in root.iterdir() if path.is_dir()} >= expected
    assert not (root / "execution.py").exists()
    assert not (root / "autonomous_execution_service.py").exists()
    assert not (root / "service.py").exists()
    assert all(audit(root / name, max_lines=350) == [] for name in expected)


def test_database_models_are_grouped() -> None:
    root = Path("app/infrastructure/database/models")
    expected = {
        "admin_auth",
        "investigation",
        "knowledge_document",
        "remediation",
        "report_analysis",
        "server",
    }

    assert {path.name for path in root.iterdir() if path.is_dir()} >= expected
    for name in expected:
        assert audit(root / name, max_lines=350) == []
    assert not (root / "remediation.py").exists()


def test_infrastructure_multi_class_modules_are_grouped() -> None:
    repository_root = Path("app/infrastructure/database/repositories")
    ssh_root = Path("app/infrastructure/ssh")

    assert (repository_root / "knowledge_retrieval_repository").is_dir()
    assert (ssh_root / "client").is_dir()
    assert (ssh_root / "command_executor").is_dir()
    assert not (repository_root / "knowledge_retrieval_repository.py").exists()
    assert not (ssh_root / "client.py").exists()
    assert not (ssh_root / "command_executor.py").exists()
    assert audit(repository_root / "knowledge_retrieval_repository", max_lines=350) == []
    assert audit(ssh_root / "client", max_lines=350) == []
    assert audit(ssh_root / "command_executor", max_lines=350) == []


def test_admin_interfaces_are_grouped() -> None:
    root = Path("app/interfaces/admin")
    schema_root = root / "schemas"

    assert all((schema_root / name).is_dir() for name in {
        "autonomous_remediation", "commands", "investigations",
        "knowledge_sources", "profiles", "remediation", "reports",
        "servers", "specialists",
    })
    assert (root / "auth").is_dir()
    assert (root / "api" / "profiles").is_dir()
    assert audit(schema_root, max_lines=350) == []
    assert audit(root / "auth", max_lines=350) == []
    assert audit(root / "api" / "profiles", max_lines=350) == []
    assert not (root / "auth.py").exists()
    assert not (root / "api" / "profiles.py").exists()


def test_claude_runtime_components_are_grouped() -> None:
    root = Path("app/runtime/claude")
    expected = {
        "models", "exceptions", "command", "runtime", "supervisor",
        "stream_decoder", "session_runner", "observability",
    }

    assert {path.name for path in root.iterdir() if path.is_dir()} >= expected
    assert all(audit(root / name, max_lines=350) == [] for name in expected)
    for name in expected:
        assert not (root / f"{name}.py").exists()


def test_composition_and_mcp_components_are_grouped() -> None:
    composition = Path("app/composition/analysis")
    mcp_schemas = Path("app/interfaces/mcp/schemas")
    mcp_definitions = Path("app/interfaces/mcp/handlers/definitions")
    mcp_investigation = Path("app/interfaces/mcp/handlers/investigation")

    assert audit(composition, max_lines=350) == []
    assert audit(mcp_schemas, max_lines=350) == []
    assert audit(mcp_definitions, max_lines=350) == []
    assert audit(mcp_investigation, max_lines=350) == []
    assert not Path("app/composition/analysis.py").exists()
    assert not Path("app/interfaces/mcp/schemas.py").exists()
    assert not Path("app/interfaces/mcp/handlers/definitions.py").exists()
    assert not Path("app/interfaces/mcp/handlers/investigation.py").exists()
