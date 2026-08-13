from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"


def _module_name(path: Path) -> str:
    relative = path.relative_to(ROOT).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)

    return {name for name in result if name == "app" or name.startswith("app.")}


def _violations(
    package: str,
    forbidden_prefixes: tuple[str, ...],
) -> list[str]:
    violations: list[str] = []
    root = ROOT / package.replace(".", "/")

    for path in root.rglob("*.py"):
        for imported in _imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(
                    f"{path.relative_to(ROOT)} -> {imported}"
                )

    return violations


def test_core_has_no_outer_layer_dependencies():
    assert _violations(
        "app/core",
        (
            "app.infrastructure",
            "app.interfaces",
            "app.composition",
            "app.capabilities",
            "app.runtime",
        ),
    ) == []


def test_capabilities_do_not_depend_on_interfaces_composition_or_runtime():
    assert _violations(
        "app/capabilities",
        (
            "app.interfaces",
            "app.composition",
            "app.runtime",
        ),
    ) == []


def test_infrastructure_does_not_depend_on_interface_or_runtime_layers():
    assert _violations(
        "app/infrastructure",
        (
            "app.interfaces",
            "app.composition",
            "app.runtime",
        ),
    ) == []


def test_transitional_shared_and_tools_packages_are_absent():
    assert not (APP / "shared").exists()
    assert not (APP / "tools").exists()


def test_application_import_graph_is_acyclic():
    module_paths = {
        _module_name(path): path
        for path in APP.rglob("*.py")
    }
    graph = {
        module: {
            imported
            for imported in _imports(path)
            if imported in module_paths
        }
        for module, path in module_paths.items()
    }

    visiting: list[str] = []
    visited: set[str] = set()
    cycles: list[str] = []

    def visit(module: str) -> None:
        if module in visiting:
            start = visiting.index(module)
            cycles.append(" -> ".join(visiting[start:] + [module]))
            return
        if module in visited:
            return

        visiting.append(module)
        for dependency in sorted(graph[module]):
            visit(dependency)
        visiting.pop()
        visited.add(module)

    for module in sorted(graph):
        visit(module)

    assert cycles == []
