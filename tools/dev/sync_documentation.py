from __future__ import annotations

from datetime import date
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
INVENTORY = DOCS / "DOCUMENTATION_INVENTORY.md"

BEGIN = "<!-- PROJECT-DOC-METADATA:BEGIN -->"
END = "<!-- PROJECT-DOC-METADATA:END -->"

TODAY = date.today().isoformat()

HISTORICAL_PATTERNS = (
    "docs/roadmap/phase-4-17-closeout.md",
    "docs/roadmap/phase-4-18-implementation.md",
    "docs/roadmap/phase-4-19-implementation.md",
    "docs/roadmap/phase-4-4-5-to-4-11-closeout.md",
    "docs/roadmap/phase-4-foundation-closeout.md",
    "docs/roadmap/phase-4-implementation-plan.md",
    "docs/roadmap/phase-4-20-implementation.md",
    "docs/roadmap/phase-4-20-closeout.md",
    "docs/roadmap/claude-runtime-implementation-plan.md",
    "docs/roadmap/c14-claude-native-execution-plan.md",
)

REFERENCE_NAMES = {
    "docs/rag_configuration.md",
    "docs/testing/performance.md",
}

CURRENT_CANONICAL = {
    "docs/PROJECT_STATUS.md",
    "docs/PROJECT_STRUCTURE.md",
    "docs/README.md",
    "docs/DOCUMENTATION_MAINTENANCE.md",
    "docs/architecture/overview.md",
    "docs/architecture/c14-12-runtime-readiness-gate.md",
    "docs/architecture/target-project-structure.md",
    "docs/testing/TESTING_STRATEGY.md",
    "docs/testing/TEST_CATALOG.md",
    "docs/testing/RUNTIME_SCENARIOS.md",
    "docs/testing/testing-and-evaluation.md",
    "docs/workflows/current-workflows.md",
    "docs/operations/running-project.md",
    "docs/operations/claude-runtime.md",
    "docs/operations/configuration.md",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def classify(path: Path) -> str:
    name = rel(path)
    text = path.read_text(encoding="utf-8")

    if name.startswith("docs/decisions/ADR-"):
        return "HISTORICAL_ADR"

    if name in HISTORICAL_PATTERNS:
        return "HISTORICAL_CLOSEOUT"

    if (
        name.startswith("docs/architecture/c14-")
        and name
        != "docs/architecture/c14-12-runtime-readiness-gate.md"
    ):
        return "HISTORICAL_CLOSEOUT"

    if name in {
        "docs/architecture/server-coordinator.md",
        "docs/architecture/cross-specialist-correlation.md",
        "docs/architecture/dynamic-secondary-specialist-routing.md",
        "docs/architecture/investigation-read-models.md",
        "docs/architecture/investigation-runtime-snapshot.md",
    }:
        return "HISTORICAL_CLOSEOUT"

    if (
        name.startswith("docs/architecture/")
        and name
        not in {
            "docs/architecture/overview.md",
            "docs/architecture/target-project-structure.md",
            "docs/architecture/c14-12-runtime-readiness-gate.md",
            "docs/architecture/database.md",
            "docs/architecture/diagnostic-policy.md",
            "docs/architecture/diagnostic-tool-registry.md",
            "docs/architecture/evidence-collection.md",
        }
        and (
            "**Phase:**" in text
            or "pending runtime" in text.casefold()
            or "future execution" in text.casefold()
        )
    ):
        return "HISTORICAL_CLOSEOUT"

    if name in REFERENCE_NAMES:
        return "REFERENCE"

    if name in CURRENT_CANONICAL:
        return "CURRENT_CANONICAL"

    if name.startswith("docs/testing/"):
        return "TESTING"

    if name.startswith(
        (
            "docs/operations/",
            "docs/deployment/",
            "docs/security/",
        )
    ):
        return "OPERATIONS"

    if name.startswith("docs/roadmap/"):
        return "ROADMAP"

    # Architecture/API/UI documents describe implemented subsystems. They are
    # current supporting references unless explicitly classified above.
    if name.startswith(
        (
            "docs/architecture/",
            "docs/api/",
            "docs/ui/",
            "docs/workflows/",
        )
    ):
        return "CURRENT_CANONICAL"

    if name.startswith("docs/decisions/"):
        return "HISTORICAL_ADR"

    return "REFERENCE"


def title(path: Path) -> str:
    text = path.read_text(
        encoding="utf-8"
    )

    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()

    return path.stem


def remove_managed_block(text: str) -> str:
    pattern = re.compile(
        re.escape(BEGIN)
        + r".*?"
        + re.escape(END),
        re.S,
    )

    return pattern.sub(
        "",
        text,
    ).rstrip()


def metadata_block(
    *,
    classification: str,
) -> str:
    return f"""
{BEGIN}
Document classification: **{classification}**

Documentation synchronized: **{TODAY}**

Canonical project state:

```text
Phase 4.20: complete
readiness: blocked_by_safe_test_environment
automatic_remediation_allowed: false
```

For current system state, see [`docs/PROJECT_STATUS.md`](/docs/PROJECT_STATUS.md).
{END}
""".strip()


def update_doc(path: Path) -> None:
   

    text = path.read_text(
        encoding="utf-8"
    )

    classification = classify(path)

    cleaned = remove_managed_block(
        text
    )

    updated = (
        cleaned
        + "\n\n"
        + metadata_block(
            classification=classification
        )
        + "\n"
    )

    path.write_text(
        updated,
        encoding="utf-8",
        newline="\n",
    )


def generate_inventory(
    docs: list[Path],
) -> None:
    rows = []

    for path in docs:
        if path == INVENTORY:
            continue

        rows.append(
            (
                rel(path),
                classify(path),
                title(path),
            )
        )

    rows.sort()

    lines = [
        "# Documentation Inventory",
        "",
        "<!-- DOC-STATUS: CURRENT -->",
        "",
        f"Generated: **{TODAY}**",
        "",
        "Every Markdown document in `docs/` is classified below.",
        "",
        "| Document | Classification | Title |",
        "|---|---|---|",
    ]

    for name, classification, doc_title in rows:
        target = name[len("docs/"):]
        lines.append(
            f"| [`{name}`]({target}) | "
            f"{classification} | "
            f"{doc_title.replace('|', '/')} |"
        )

    lines.extend(
        [
            "",
            "## Classification meanings",
            "",
            "- **CURRENT** — active description/instructions for the current system.",
            "- **HISTORICAL** — preserved implementation/closeout history; body may intentionally mention earlier phases.",
            "- **DECISION** — accepted ADR; preserved as a decision record.",
            "- **REFERENCE** — supporting reference material.",
            "",
        ]
    )

    INVENTORY.write_text(
        "\n".join(lines),
        encoding="utf-8",
        newline="\n",
    )

    # Inventory itself also gets the standard metadata.
    update_doc(INVENTORY)


def main() -> int:
    docs = sorted(
        path
        for path in DOCS.rglob("*.md")
        if path.is_file()
    )

    for path in docs:
        update_doc(path)

    # Re-scan in case files were added immediately before sync.
    docs = sorted(
        path
        for path in DOCS.rglob("*.md")
        if path.is_file()
    )

    generate_inventory(docs)

    print(
        f"Synchronized documentation: "
        f"{len(docs)} Markdown files"
    )
    print(
        f"Generated: "
        f"{INVENTORY.relative_to(ROOT)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
