from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SMOKE = ROOT / "tools" / "acceptance" / "smoke_ollama_claude_runtime.py"


def test_c14_7_smoke_initializes_schema_before_container():
    text = SMOKE.read_text(encoding="utf-8")

    assert (
        "from app.infrastructure.database.engine import ("
        in text
    )
    assert "create_database_tables," in text
    assert "def prepare_database_schema()" in text

    schema_call = text.index(
        "    prepare_database_schema()"
    )
    container_call = text.index(
        "    container = build_container()"
    )

    assert schema_call < container_call


def test_c14_7_smoke_preserves_direct_project_import_fix():
    text = SMOKE.read_text(encoding="utf-8")

    assert (
        "PROJECT_ROOT = Path(__file__).resolve().parents[2]"
        in text
    )
    assert "sys.path.insert(0, PROJECT_ROOT_TEXT)" in text
