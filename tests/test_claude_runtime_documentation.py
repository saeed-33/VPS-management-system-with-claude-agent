from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_doc(
    relative_path: str,
) -> str:
    return (
        ROOT
        / relative_path
    ).read_text(
        encoding="utf-8",
    )


def test_project_structure_documents_runtime_files():
    project_structure = read_doc(
        "docs/PROJECT_STRUCTURE.md"
    )

    required_entries = [
        "CLAUDE.md",
        ".mcp.json",
        ".claude/settings.json",
        "app/runtime/claude/supervisor.py",
        "app/tools/project_boundary.py",
        "app/tools/catalog.py",
        "app/admin/api/system.py",
        "app/admin/web/templates/system.html",
        "docs/operations/claude-runtime.md",
    ]

    for entry in required_entries:
        assert entry in project_structure


def test_runtime_operations_doc_matches_configured_ollama_defaults():
    runtime_doc = read_doc(
        "docs/operations/claude-runtime.md"
    )
    config_doc = read_doc(
        "docs/operations/configuration.md"
    )
    env_example = read_doc(
        ".env.example"
    )

    assert "OLLAMA_MODEL=qwen3:8b" in runtime_doc
    assert "ollama pull qwen3:8b" in runtime_doc
    assert "OLLAMA_MODEL=qwen3:8b" in config_doc
    assert "OLLAMA_MODEL=qwen3:8b" in env_example


def test_runtime_documentation_has_current_verification_commands():
    runtime_doc = read_doc(
        "docs/operations/claude-runtime.md"
    )

    assert "app\\runtime" in runtime_doc
    assert "app\\tools" in runtime_doc
    assert "app\\integrations" not in runtime_doc


def test_r5_status_and_test_catalog_are_documented():
    roadmap = read_doc(
        "docs/roadmap/claude-runtime-implementation-plan.md"
    )
    status = read_doc(
        "docs/PROJECT_STATUS.md"
    )
    test_catalog = read_doc(
        "docs/testing/TEST_CATALOG.md"
    )

    assert "R.5 - Documentation and Tests" in roadmap
    assert "R.5 Documentation and Tests: complete" in status
    assert (
        "tests/test_claude_runtime_documentation.py"
        in test_catalog
    )
