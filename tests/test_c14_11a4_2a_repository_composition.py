from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_repository_construction_lives_in_repository_composition_module():
    builder = (
        ROOT / "app/composition/builder.py"
    ).read_text(encoding="utf-8")
    repositories = (
        ROOT / "app/composition/repositories.py"
    ).read_text(encoding="utf-8")

    assert "repositories = build_repositories()" in builder
    assert "class RepositoryBundle" in repositories
    assert "def build_repositories()" in repositories

    constructor_names = [
        "ServerRepository",
        "CommandRepository",
        "MonitoringProfileRepository",
        "ReportRepository",
        "AnalysisRepository",
        "RetrievalRepository",
        "AnalysisSourceRepository",
        "SpecialistDefinitionRepository",
        "InvestigationRepository",
        "KnowledgeSourceRepository",
        "KnowledgeDocumentRepository",
        "AgentJobRepository",
        "RemediationRepository",
    ]

    import ast

    builder_tree = ast.parse(builder)
    repository_tree = ast.parse(repositories)

    builder_calls = {
        node.func.id
        for node in ast.walk(builder_tree)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
        )
    }
    repository_calls = {
        node.func.id
        for node in ast.walk(repository_tree)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
        )
    }

    for constructor_name in constructor_names:
        assert constructor_name not in builder_calls
        assert constructor_name in repository_calls


def test_repository_composition_module_is_not_eager():
    repositories = (
        ROOT / "app/composition/repositories.py"
    ).read_text(encoding="utf-8")

    assert "\nrepositories = build_repositories()" not in repositories
