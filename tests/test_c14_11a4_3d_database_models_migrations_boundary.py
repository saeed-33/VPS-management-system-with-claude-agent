from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]


def test_database_models_live_in_infrastructure():
    old_root = ROOT / "app/shared/database/models"
    new_root = ROOT / "app/infrastructure/database/models"

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
        old_text = (old_root / name).read_text(encoding="utf-8")
        new_text = (new_root / name).read_text(encoding="utf-8")

        assert not any(
            isinstance(node, (ast.ClassDef, ast.FunctionDef))
            for node in ast.parse(old_text).body
        )
        assert any(
            isinstance(node, ast.ClassDef)
            for node in ast.parse(new_text).body
        )


def test_production_uses_infrastructure_model_imports():
    violations = []

    for path in (ROOT / "app").rglob("*.py"):
        relative = path.relative_to(ROOT)

        if relative.parts[:4] == (
            "app", "shared", "database", "models"
        ):
            continue

        text = path.read_text(encoding="utf-8")

        if "app.shared.database.models" in text:
            violations.append(str(relative))

    assert violations == []


def test_engine_registers_infrastructure_models():
    text = (
        ROOT / "app/infrastructure/database/engine.py"
    ).read_text(encoding="utf-8")

    assert "import app.infrastructure.database.models" in text
    assert "import app.shared.database.models" not in text


def test_migrations_are_identical_compatibility_mirrors():
    old_root = ROOT / "app/shared/database/migrations"
    new_root = ROOT / "app/infrastructure/database/migrations"

    old_files = {
        p.relative_to(old_root)
        for p in old_root.rglob("*")
        if p.is_file()
    }
    new_files = {
        p.relative_to(new_root)
        for p in new_root.rglob("*")
        if p.is_file()
    }

    assert old_files
    assert old_files == new_files

    for relative in sorted(old_files):
        assert (
            old_root / relative
        ).read_bytes() == (
            new_root / relative
        ).read_bytes()
