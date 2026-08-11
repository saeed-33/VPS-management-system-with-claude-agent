from __future__ import annotations

import ast
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "PROJECT_STRUCTURE.md"

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "artifacts",
}

EXCLUDED_PREFIXES = (
    ".step_",
)

SPECIAL = {
    "app/main.py": (
        "FastAPI application entry point; "
        "registers API/web routers and startup/shutdown behavior."
    ),
    "app/bootstrap.py": (
        "Application composition root / dependency container. "
        "Builds repositories, services, LLM clients, registries, "
        "Policy, coordinators, and shared runtime dependencies."
    ),
    "app/shared/config.py": (
        "Environment-backed application configuration."
    ),
    "pyproject.toml": (
        "Python project metadata and dependency configuration."
    ),
    "pytest.ini": (
        "Pytest configuration."
    ),
    ".env.example": (
        "Example environment variables for local/runtime configuration."
    ),
    "README.md": (
        "Top-level project overview and startup guidance."
    ),
}


def should_skip(path: Path) -> bool:
    parts = path.relative_to(ROOT).parts

    if any(
        part in EXCLUDED_DIRS
        for part in parts
    ):
        return True

    if any(
        part.startswith(
            EXCLUDED_PREFIXES
        )
        for part in parts
    ):
        return True

    return False


def python_summary(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()

    if rel in SPECIAL:
        return SPECIAL[rel]

    try:
        text = path.read_text(
            encoding="utf-8"
        )
        tree = ast.parse(text)
    except Exception:
        return "Python module."

    doc = ast.get_docstring(tree)
    if doc:
        return doc.strip().split(
            "\n",
            1,
        )[0]

    names = []

    for node in tree.body:
        if isinstance(
            node,
            ast.ClassDef,
        ):
            names.append(
                f"class `{node.name}`"
            )
        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ) and not node.name.startswith("_"):
            names.append(
                f"`{node.name}()`"
            )

    if rel.startswith(
        "tests/"
    ):
        return (
            "Pytest coverage for "
            + (
                ", ".join(
                    names[:5]
                )
                if names
                else "the corresponding project behavior"
            )
            + "."
        )

    if rel.startswith(
        "tools/"
    ):
        return (
            "Operator/developer tool"
            + (
                " exposing "
                + ", ".join(
                    names[:4]
                )
                if names
                else ""
            )
            + "."
        )

    if "/repositories/" in rel:
        return (
            "Persistence repository module"
            + (
                " containing "
                + ", ".join(
                    names[:4]
                )
                if names
                else ""
            )
            + "."
        )

    if "/services/" in rel:
        return (
            "Service-layer module"
            + (
                " containing "
                + ", ".join(
                    names[:4]
                )
                if names
                else ""
            )
            + "."
        )

    if "/schemas/" in rel:
        return (
            "API/schema models"
            + (
                " including "
                + ", ".join(
                    names[:5]
                )
                if names
                else ""
            )
            + "."
        )

    if "/api/" in rel:
        return (
            "FastAPI API router/module"
            + (
                " exposing "
                + ", ".join(
                    names[:4]
                )
                if names
                else ""
            )
            + "."
        )

    if "/evaluation/" in rel:
        return (
            "Phase 4.20 evaluation/readiness component"
            + (
                " containing "
                + ", ".join(
                    names[:5]
                )
                if names
                else ""
            )
            + "."
        )

    if "/investigation/" in rel:
        return (
            "Autonomous Investigation subsystem module"
            + (
                " containing "
                + ", ".join(
                    names[:5]
                )
                if names
                else ""
            )
            + "."
        )

    return (
        "Python module"
        + (
            " containing "
            + ", ".join(
                names[:5]
            )
            if names
            else ""
        )
        + "."
    )


def describe(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()

    if rel in SPECIAL:
        return SPECIAL[rel]

    suffix = path.suffix.lower()

    if suffix == ".py":
        return python_summary(path)

    if suffix in {
        ".md",
        ".rst",
    }:
        return "Project documentation."

    if suffix in {
        ".html",
    }:
        return "Jinja/HTML administration UI template."

    if suffix == ".css":
        return "Administration UI stylesheet."

    if suffix == ".js":
        return "Administration UI browser-side JavaScript."

    if suffix in {
        ".toml",
        ".ini",
        ".cfg",
    }:
        return "Project/tool configuration."

    if suffix in {
        ".json",
        ".yaml",
        ".yml",
    }:
        return "Structured configuration or generated data."

    if path.name.startswith(
        "alembic"
    ) or "migration" in rel.lower():
        return "Database migration/configuration asset."

    if suffix == ".sql":
        return "SQL/database asset."

    if suffix == ".txt":
        return "Text data/documentation asset."

    return "Project asset."


def group(rel: str) -> str:
    if rel.startswith("app/admin/"):
        return "Administration API and Web UI"
    if rel.startswith(
        "app/agent/evaluation/"
    ):
        return "Evaluation and Production Readiness"
    if rel.startswith(
        "app/agent/investigation/"
    ):
        return "Autonomous Investigation"
    if rel.startswith("app/agent/"):
        return "Agent / Analysis"
    if rel.startswith("app/shared/"):
        return "Shared application layer"
    if rel.startswith("app/"):
        return "Application core"
    if rel.startswith("tests/"):
        return "Tests"
    if rel.startswith("tools/"):
        return "Tools and acceptance scripts"
    if rel.startswith("docs/"):
        return "Documentation"
    return "Repository root / configuration"


def main() -> int:
    files = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue

        rel = path.relative_to(ROOT).as_posix()

        # Do not document generated backup/package artifacts.
        if rel == OUTPUT.relative_to(ROOT).as_posix():
            continue

        files.append(
            (
                rel,
                describe(path),
            )
        )

    files.sort()

    grouped = {}

    for rel, description in files:
        grouped.setdefault(
            group(rel),
            [],
        ).append(
            (
                rel,
                description,
            )
        )

    lines = [
        "# Project Structure and File Responsibilities",
        "",
        "This document is generated from the current checkout.",
        "",
        "Regenerate with:",
        "",
        "```powershell",
        "uv run python tools/generate_project_structure.py",
        "```",
        "",
        "## Architectural flow",
        "",
        "```text",
        "Server / Monitoring Profile",
        "        ↓",
        "Monitoring execution",
        "        ↓",
        "Report",
        "        ↓",
        "Analysis",
        "        ↓",
        "Investigation Router",
        "        ↓",
        "LangGraph Coordinator",
        "        ↓",
        "Specialist loops + Policy + SSH diagnostic tools",
        "        ↓",
        "Evidence",
        "        ↓",
        "Cross-Specialist Correlation",
        "        ↓",
        "Final Diagnosis + Narrative",
        "        ↓",
        "Runtime Snapshot Persistence",
        "        ↓",
        "API / Administration UI",
        "        ↓",
        "Evaluation / Production Readiness Gate",
        "```",
        "",
        "## File-by-file inventory",
        "",
    ]

    preferred_order = (
        "Repository root / configuration",
        "Application core",
        "Administration API and Web UI",
        "Agent / Analysis",
        "Autonomous Investigation",
        "Evaluation and Production Readiness",
        "Shared application layer",
        "Tools and acceptance scripts",
        "Tests",
        "Documentation",
    )

    for section in preferred_order:
        items = grouped.get(
            section,
            [],
        )

        if not items:
            continue

        lines.append(
            f"### {section}"
        )
        lines.append("")

        for rel, description in items:
            lines.append(
                f"- `{rel}` — {description}"
            )

        lines.append("")

    lines.extend(
        [
            "## Maintenance rule",
            "",
            "Regenerate this document whenever files are added, removed, or substantially repurposed. "
            "Descriptions are derived from path conventions, module docstrings, and public classes/functions; "
            "core files have explicit descriptions in the generator.",
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
        f"{OUTPUT.relative_to(ROOT)} "
        f"({len(files)} files)"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
