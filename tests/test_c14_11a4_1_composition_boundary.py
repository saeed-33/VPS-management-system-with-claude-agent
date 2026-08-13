from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_composition_owns_the_application_container():
    composition = ROOT / "app/composition/__init__.py"
    text = composition.read_text(encoding="utf-8")

    assert "container = build_container()" in text
    assert '"container"' in text
    assert not (ROOT / "app/bootstrap.py").exists()


def test_composition_builder_owns_dependency_wiring():
    builder = ROOT / "app/composition/builder.py"
    builder_text = builder.read_text(encoding="utf-8")

    container = ROOT / "app/composition/container.py"
    container_text = container.read_text(encoding="utf-8")

    assert (
        "from app.composition.container import ApplicationContainer"
        in builder_text
    )
    assert "class ApplicationContainer" not in builder_text
    assert "class ApplicationContainer" in container_text

    assert "def build_container()" in builder_text
    assert "return ApplicationContainer(" in builder_text

    assert "\ncontainer = build_container()" not in builder_text



def test_composition_package_exists_as_explicit_boundary():
    init_file = ROOT / "app/composition/__init__.py"
    text = init_file.read_text(encoding="utf-8")

    assert "ApplicationContainer" in text
    assert "build_container" in text
