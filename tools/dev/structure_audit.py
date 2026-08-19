"""Static audit for the project's source-file structure rules.

The audit intentionally has no project-specific imports.  It can therefore run
before the application is importable and can be used while modules are being
moved during the structural refactor.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path


DEFAULT_MAX_LINES = 350
IGNORED_DIRECTORY_NAMES = {"__pycache__", ".venv", ".git"}


def iter_python_files(root: Path) -> list[Path]:
    """Return deterministic Python source paths below ``root``."""
    return [
        path
        for path in sorted(root.rglob("*.py"))
        if not any(part in IGNORED_DIRECTORY_NAMES for part in path.parts)
    ]


def top_level_class_names(tree: ast.Module) -> list[str]:
    """Return classes declared directly by a module, in source order."""
    return [
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    ]


def audit(root: Path, *, max_lines: int | None = DEFAULT_MAX_LINES) -> list[dict[str, object]]:
    """Collect structural violations below ``root``.

    The first migration rule is deliberately limited to top-level classes:
    nested helper classes are implementation details of their owning class and
    do not create another module-level public owner.
    """
    violations: list[dict[str, object]] = []

    for path in iter_python_files(root):
        relative_path = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8")

        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as error:
            violations.append(
                {
                    "kind": "syntax_error",
                    "path": relative_path,
                    "detail": f"line {error.lineno}: {error.msg}",
                }
            )
            continue

        class_names = top_level_class_names(tree)
        if len(class_names) > 1:
            violations.append(
                {
                    "kind": "multiple_top_level_classes",
                    "path": relative_path,
                    "count": len(class_names),
                    "classes": tuple(class_names),
                }
            )

        line_count = len(source.splitlines())
        if max_lines is not None and line_count > max_lines:
            violations.append(
                {
                    "kind": "file_too_large",
                    "path": relative_path,
                    "lines": line_count,
                    "limit": max_lines,
                }
            )

    return sorted(violations, key=lambda item: (str(item["path"]), str(item["kind"])))


def _summary(root: Path, violations: list[dict[str, object]]) -> str:
    files = iter_python_files(root)
    class_count = 0
    for path in files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue
        class_count += len(top_level_class_names(tree))

    counts: dict[str, int] = {}
    for violation in violations:
        kind = str(violation["kind"])
        counts[kind] = counts.get(kind, 0) + 1

    return "\n".join(
        (
            f"Structure audit: {root}",
            f"Files scanned: {len(files)}",
            f"Top-level classes: {class_count}",
            f"Violations: {len(violations)}",
            f"  multiple_top_level_classes: {counts.get('multiple_top_level_classes', 0)}",
            f"  file_too_large: {counts.get('file_too_large', 0)}",
            f"  syntax_error: {counts.get('syntax_error', 0)}",
        )
    )


def _format_violation(violation: dict[str, object]) -> str:
    kind = str(violation["kind"])
    path = str(violation["path"])
    if kind == "multiple_top_level_classes":
        classes = ", ".join(str(name) for name in violation["classes"])
        return f"{path}: {kind} ({classes})"
    if kind == "file_too_large":
        return f"{path}: {kind} ({violation['lines']} > {violation['limit']} lines)"
    return f"{path}: {kind} ({violation['detail']})"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("app"))
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return exit code 1 when any structural violation is found",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    violations = audit(root, max_lines=args.max_lines)
    print(_summary(root, violations))
    for violation in violations:
        print(f"- {_format_violation(violation)}")

    return 1 if args.strict and violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
