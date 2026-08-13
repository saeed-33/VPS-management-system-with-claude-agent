from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]


def test_database_core_implementation_lives_in_infrastructure():
    infra = ROOT / "app/infrastructure/database"
    for name in ("base.py", "engine.py", "session.py"):
        path = infra / name
        assert path.is_file()
        assert path.read_text(encoding="utf-8").strip()


def test_repository_implementations_live_in_infrastructure():
    old_root = ROOT / "app/shared/database/repositories"
    new_root = ROOT / "app/infrastructure/database/repositories"

    old_files = {
        p.name for p in old_root.glob("*.py")
        if p.name != "__init__.py"
    }
    new_files = {
        p.name for p in new_root.glob("*.py")
        if p.name != "__init__.py"
    }

    assert old_files
    assert old_files == new_files

    for name in sorted(new_files):
        old_tree = ast.parse(
            (old_root / name).read_text(encoding="utf-8")
        )
        new_tree = ast.parse(
            (new_root / name).read_text(encoding="utf-8")
        )

        assert not any(
            isinstance(node, ast.ClassDef)
            for node in old_tree.body
        )
        assert any(
            isinstance(node, (ast.ClassDef, ast.FunctionDef))
            for node in new_tree.body
        )


def test_production_composition_uses_infrastructure_repositories():
    text = (
        ROOT / "app/composition/repositories.py"
    ).read_text(encoding="utf-8")

    assert "app.infrastructure.database.repositories" in text
    assert "app.shared.database.repositories" not in text


def test_shared_database_core_paths_are_facades():
    for name in ("base.py", "engine.py", "session.py"):
        text = (
            ROOT / "app/shared/database" / name
        ).read_text(encoding="utf-8")

        tree = ast.parse(text)
        assert not any(
            isinstance(node, (ast.ClassDef, ast.FunctionDef))
            for node in tree.body
        )
        assert "app.infrastructure.database" in text


def test_models_and_migrations_remain_deferred():
    assert (ROOT / "app/shared/database/models").is_dir()
    assert (ROOT / "app/shared/database/migrations").is_dir()
