from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TESTS = ROOT / "tests"
TOOLS = ROOT / "tools"
OUTPUT = (
    ROOT
    / "docs"
    / "testing"
    / "TEST_CATALOG.md"
)


def first_docstring(path: Path) -> str:
    try:
        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return ""

    return (
        ast.get_docstring(tree)
        or ""
    ).strip().split(
        "\n",
        1,
    )[0]


def test_functions(path: Path):
    try:
        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return []

    return [
        node.name
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name.startswith(
            "test_"
        )
    ]


def main() -> int:
    lines = [
        "# Complete Test Catalog",
        "",
        "Generated from the current checkout.",
        "",
        "Regenerate with:",
        "",
        "```powershell",
        "uv run python tools/dev/generate_test_catalog.py",
        "```",
        "",
        "## Pytest files",
        "",
    ]

    test_files = sorted(
        TESTS.glob(
            "test_*.py"
        )
    )

    for path in test_files:
        rel = path.relative_to(ROOT)
        funcs = test_functions(path)

        lines.append(
            f"### `{rel.as_posix()}`"
        )
        lines.append("")

        if funcs:
            for name in funcs:
                lines.append(
                    f"- `{name}`"
                )
        else:
            lines.append(
                "- No top-level `test_*` "
                "function discovered "
                "(may use classes/fixtures)."
            )

        lines.append("")

    lines.extend(
        [
            "## Runtime / acceptance tools",
            "",
        ]
    )

    tool_files = sorted(
        {
            *TOOLS.glob(
                "run_*.py"
            ),
            *TOOLS.glob(
                "list_*.py"
            ),
        }
    )

    for path in tool_files:
        rel = path.relative_to(ROOT)
        summary = first_docstring(path)

        lines.append(
            f"- `{rel.as_posix()}`"
            + (
                f" — {summary}"
                if summary
                else ""
            )
        )

    lines.extend(
        [
            "",
            "## Standard commands",
            "",
            "```powershell",
            "uv run python -m pytest",
            "uv run python tools/dev/list_routes.py",
            "uv run python tools/acceptance/run_evaluation_dataset.py",
            "uv run python tools/acceptance/run_safety_runtime_evaluation.py",
            "uv run python tools/acceptance/run_persisted_runtime_evaluation.py --limit 500",
            "uv run python tools/acceptance/run_production_readiness_evaluation.py --limit 500",
            "```",
            "",
            "See `TESTING_STRATEGY.md` for when each layer is required.",
            "",
        ]
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        "\n".join(lines),
        encoding="utf-8",
        newline="\n",
    )

    print(
        f"Generated: "
        f"{OUTPUT.relative_to(ROOT)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
