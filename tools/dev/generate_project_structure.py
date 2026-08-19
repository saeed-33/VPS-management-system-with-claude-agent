"""
أداة تطوير/تشخيص لتشغيل workflow أو فحص contracts والبيانات أثناء التطوير.

الموقع في المعمارية: Developer tooling.
يُستدعى بواسطة: CLI أو المطور مباشرة.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: ليست application boundary ولا ينبغي اعتبارها API production.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import ast
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
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
    "CLAUDE.md": (
        "Claude project instruction entrypoint loaded at session start; "
        "defines architecture, workflow, and coding rules."
    ),
    ".mcp.json": (
        "Claude MCP configuration exposing project tool servers."
    ),
    ".claude/settings.json": (
        "Claude project settings for permissions, tools, and hooks."
    ),
    ".claude/hooks/README.md": (
        "Documents Claude hook responsibilities and safety checks."
    ),
    ".claude/agents/monitoring-supervisor.md": (
        "Claude subagent role definition for scheduled monitoring supervision."
    ),
    ".claude/agents/investigation-coordinator.md": (
        "Claude subagent role definition for server-level investigation coordination."
    ),
    ".claude/agents/generic-specialist.md": (
        "Generic Claude specialist role; uses project tools and DB-managed specialist definitions."
    ),
    ".claude/commands/monitor.md": (
        "Claude slash command for executing the fixed monitoring workflow."
    ),
    ".claude/commands/analyze.md": (
        "Claude slash command for report analysis and historical retrieval workflow."
    ),
    ".claude/commands/investigate.md": (
        "Claude slash command for starting and coordinating investigations."
    ),
    ".claude/commands/diagnose.md": (
        "Claude slash command for diagnosis synthesis from persisted evidence."
    ),
    ".claude/rules/monitoring.md": (
        "Claude rule file for monitoring workflow constraints."
    ),
    ".claude/rules/rag.md": (
        "Claude rule file for exact reuse, top-3 similarity context, and retrieval grounding."
    ),
    ".claude/rules/investigation.md": (
        "Claude rule file for the fixed investigation workflow."
    ),
    ".claude/rules/specialists.md": (
        "Claude rule file for specialist selection, execution, and aggregation."
    ),
    ".claude/rules/remediation.md": (
        "Claude rule file for remediation proposal, sandbox validation, and approval."
    ),
    ".claude/rules/safety.md": (
        "Claude rule file for tool safety, policy boundaries, and prohibited bypasses."
    ),
    ".claude/skills/monitor-server/SKILL.md": (
        "Claude skill instructions for server monitoring tasks."
    ),
    ".claude/skills/analyze-incident/SKILL.md": (
        "Claude skill instructions for incident report analysis."
    ),
    ".claude/skills/investigate-incident/SKILL.md": (
        "Claude skill instructions for specialist investigation workflows."
    ),
    ".claude/skills/plan-remediation/SKILL.md": (
        "Claude skill instructions for remediation planning and validation."
    ),
    "docs/architecture/target-project-structure.md": (
        "Current architecture map for Claude runtime, capabilities, infrastructure, MCP, and admin UI."
    ),
    "docs/operations/claude-runtime.md": (
        "Operational guide for running the API, Ollama, and Claude Code runtime."
    ),
    "docs/roadmap/claude-runtime-implementation-plan.md": (
        "Implementation plan for Claude runtime, tool boundaries, package layout, documentation, and tests."
    ),
    "app/main.py": (
        "FastAPI application entry point; "
        "registers API/web routers and startup/shutdown behavior."
    ),
    "app/composition/__init__.py": (
        "Application composition root / dependency container. "
        "Exports the canonical wired application container."
    ),
    "app/interfaces/mcp/registry.py": (
        "Project tool execution boundary used by Claude through MCP; "
        "validates calls, invokes deterministic services, and returns structured results."
    ),
    "app/interfaces/mcp/catalog.py": (
        "Categorizes project tools into monitoring, reports, retrieval, investigation, specialists, and remediation groups."
    ),
    "app/interfaces/mcp/schemas.py": (
        "Stable MCP request and response contracts exposed to Claude Code."
    ),
    "app/interfaces/mcp/server.py": (
        "Project-scoped MCP protocol server exposing project tools to Claude Code."
    ),
    "docs/architecture/code-structure-rules.md": (
        "Rules and audit baseline for one-class-per-file contract organization."
    ),
    "app/core/contracts/investigation/__init__.py": (
        "Provider- and infrastructure-independent investigation contracts."
    ),
    "app/core/policies/diagnostic_policy.py": (
        "Fail-closed diagnostic policy enforcement."
    ),
    "app/infrastructure/ssh/client.py": (
        "Known-hosts-verified SSH transport with validated private keys."
    ),
    "app/infrastructure/ssh/command_executor.py": (
        "Bounded SSH command execution and result contract."
    ),
    "tools/run_project_mcp_server.py": (
        "Stdio entrypoint used by .mcp.json to run the project MCP server."
    ),
    "app/core/config.py": (
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
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى should_skip؛ المدخلات المهمة: path.
    تعيد bool أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى python_summary؛ المدخلات المهمة: path.
    تعيد str أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
            "Runtime evaluation/readiness component"
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
            "Investigation domain module"
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

    if "/analysis/" in rel:
        return (
            "Analysis domain module"
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

    if "/knowledge/" in rel:
        return (
            "Knowledge domain module"
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

    if "/runtime/claude/" in rel:
        return (
            "Claude runtime module"
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

    if "/tools/monitoring/" in rel:
        return (
            "Monitoring tool module"
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

    if "/tools/ssh/" in rel:
        return (
            "SSH tool module"
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
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى describe؛ المدخلات المهمة: path.
    تعيد str أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى group؛ المدخلات المهمة: rel.
    تعيد str أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    if rel.startswith("app/interfaces/admin/"):
        return "Administration API and Web UI"
    if rel.startswith("tools/acceptance/evaluation/"):
        return "Evaluation and Production Readiness"
    if rel.startswith(
        "app/capabilities/investigation/"
    ):
        return "Investigation Domain"
    if rel.startswith("app/capabilities/knowledge/"):
        return "Knowledge Domain"
    if rel.startswith("app/capabilities/analysis/"):
        return "Analysis Domain"
    if rel.startswith("app/capabilities/monitoring/"):
        return "Monitoring Capability"
    if rel.startswith("app/infrastructure/ssh/"):
        return "SSH Infrastructure"
    if rel.startswith("app/runtime/claude/"):
        return "Claude Runtime"
    if rel.startswith("app/core/"):
        return "Core contracts, policies, and configuration"
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
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    files = []

    # os.walk lets us prune excluded directories before descending into them.
    # This is important on Windows where .venv/lib64 may be a symlink.
    for current_root, directories, filenames in os.walk(ROOT, topdown=True):
        directories[:] = [
            name
            for name in directories
            if name not in EXCLUDED_DIRS
            and not name.startswith(EXCLUDED_PREFIXES)
        ]
        for filename in filenames:
            path = Path(current_root) / filename
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
        "uv run python tools/dev/generate_project_structure.py",
        "```",
        "",
        "## Architectural flow",
        "",
        "```text",
        "Periodic Monitoring / Scheduler",
        "        ↓",
        "ClaudeSupervisor",
        "        ↓",
        "Native Claude Code CLI + Ollama",
        "        ↓",
        "vps MCP / bounded project tools",
        "        ↓",
        "Monitoring Report + PostgreSQL persistence",
        "        ↓",
        "Exact reuse or similar retrieval + Analysis",
        "        ↓",
        "Optional Investigation + DB-defined Specialists",
        "        ↓",
        "Policy + budgets + known-hosts SSH + Evidence",
        "        ↓",
        "Correlation + Final Diagnosis",
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
        "Claude Runtime",
        "Monitoring Capability",
        "SSH Infrastructure",
        "Analysis Domain",
        "Investigation Domain",
        "Knowledge Domain",
        "Evaluation and Production Readiness",
        "Administration API and Web UI",
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
