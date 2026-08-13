from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]


def test_database_core_implementation_lives_in_infrastructure():
    infra = ROOT / "app/infrastructure/database"
    for name in ("base.py", "engine.py", "session.py"):
        path = infra / name
        assert path.is_file()
        assert path.read_text(encoding="utf-8").strip()


def test_repository_implementations_live_only_in_infrastructure():
    infra_root = ROOT / "app/infrastructure/database/repositories"
    shared_root = ROOT / "app/shared/database/repositories"

    infra_files = {
        p.name for p in infra_root.glob("*.py")
        if p.name != "__init__.py"
    }

    assert infra_files
    assert not shared_root.exists()

    for name in sorted(infra_files):
        tree = ast.parse(
            (infra_root / name).read_text(encoding="utf-8")
        )
        assert any(
            isinstance(node, (ast.ClassDef, ast.FunctionDef))
            for node in tree.body
        )


def test_production_composition_uses_infrastructure_repositories():
    text = (
        ROOT / "app/composition/repositories.py"
    ).read_text(encoding="utf-8")

    assert "app.infrastructure.database.repositories" in text
    assert "app.shared.database.repositories" not in text


def test_shared_database_package_is_removed_after_boundary_closure():
    assert not (ROOT / "app/shared/database").exists()
