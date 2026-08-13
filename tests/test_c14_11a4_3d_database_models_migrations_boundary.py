from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]


def test_database_models_live_only_in_infrastructure():
    old_root = ROOT / "app/shared/database/models"
    new_root = ROOT / "app/infrastructure/database/models"

    new_files = {
        p.name for p in new_root.glob("*.py")
        if p.name != "__init__.py"
    }

    assert new_files
    assert not old_root.exists()

    for name in sorted(new_files):
        tree = ast.parse(
            (new_root / name).read_text(encoding="utf-8")
        )
        assert any(
            isinstance(node, ast.ClassDef)
            for node in tree.body
        )


def test_production_uses_infrastructure_model_imports():
    violations = []

    for path in (ROOT / "app").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "app.shared.database.models" in text:
            violations.append(str(path.relative_to(ROOT)))

    assert violations == []


def test_engine_registers_infrastructure_models():
    text = (
        ROOT / "app/infrastructure/database/engine.py"
    ).read_text(encoding="utf-8")

    assert "import app.infrastructure.database.models" in text
    assert "import app.shared.database.models" not in text


def test_migrations_have_one_canonical_owner():
    old_root = ROOT / "app/shared/database/migrations"
    new_root = ROOT / "app/infrastructure/database/migrations"

    new_files = {
        p.relative_to(new_root)
        for p in new_root.rglob("*")
        if p.is_file()
    }

    assert new_files
    assert not old_root.exists()
