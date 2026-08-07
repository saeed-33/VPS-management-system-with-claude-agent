from __future__ import annotations

from datetime import datetime
from pathlib import Path
import ast
import shutil
import sys


ROOT = Path(__file__).resolve().parent
BOOTSTRAP = ROOT / "app" / "bootstrap.py"
BACKUP = (
    ROOT
    / ".step_4_3_1_backup"
    / datetime.now().strftime("%Y%m%d_%H%M%S")
)


WRONG_REPORT_ANALYZER_BLOCK = """                report_query_service=report_query_service,
        specialist_definition_service=(
            specialist_definition_service
        ),
"""

CORRECT_REPORT_ANALYZER_BLOCK = """                report_query_service=report_query_service,
"""

APPLICATION_CONTAINER_MARKER = """        report_query_service=report_query_service,
        ssh_test_service=ssh_test_service,
"""

APPLICATION_CONTAINER_FIXED = """        report_query_service=report_query_service,
        specialist_definition_service=(
            specialist_definition_service
        ),
        ssh_test_service=ssh_test_service,
"""


def backup_file(path: Path) -> None:
    destination = BACKUP / path.relative_to(ROOT)
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    shutil.copy2(path, destination)


def main() -> int:
    if not (ROOT / "app" / "main.py").exists():
        print(
            "ERROR: run this fixer from the project root.",
            file=sys.stderr,
        )
        return 1

    if not BOOTSTRAP.exists():
        print(
            "ERROR: app/bootstrap.py was not found.",
            file=sys.stderr,
        )
        return 1

    text = BOOTSTRAP.read_text(
        encoding="utf-8"
    )
    original = text

    wrong_count = text.count(
        WRONG_REPORT_ANALYZER_BLOCK
    )

    if wrong_count > 1:
        print(
            "ERROR: found more than one unexpected "
            "specialist service injection near "
            "ReportAnalyzer.",
            file=sys.stderr,
        )
        return 1

    if wrong_count == 1:
        text = text.replace(
            WRONG_REPORT_ANALYZER_BLOCK,
            CORRECT_REPORT_ANALYZER_BLOCK,
            1,
        )
        print(
            "Fixed: removed specialist_definition_service "
            "from ReportAnalyzer(...)"
        )
    else:
        print(
            "Info: erroneous ReportAnalyzer argument "
            "was not present."
        )

    if (
        APPLICATION_CONTAINER_FIXED
        not in text
    ):
        if (
            APPLICATION_CONTAINER_MARKER
            not in text
        ):
            print(
                "ERROR: could not locate the "
                "ApplicationContainer return block.",
                file=sys.stderr,
            )
            return 1

        text = text.replace(
            APPLICATION_CONTAINER_MARKER,
            APPLICATION_CONTAINER_FIXED,
            1,
        )

        print(
            "Fixed: added specialist_definition_service "
            "to ApplicationContainer(...)"
        )
    else:
        print(
            "Info: ApplicationContainer already receives "
            "specialist_definition_service."
        )

    # Contract checks before writing.
    if (
        "specialist_definition_service: "
        "SpecialistDefinitionService"
        not in text
    ):
        print(
            "ERROR: ApplicationContainer dataclass does "
            "not define specialist_definition_service.",
            file=sys.stderr,
        )
        return 1

    if (
        "specialist_definition_service = (\n"
        "        SpecialistDefinitionService("
        not in text
    ):
        print(
            "ERROR: SpecialistDefinitionService is not "
            "constructed in build_container().",
            file=sys.stderr,
        )
        return 1

    if text == original:
        print(
            "No changes were required."
        )
    else:
        backup_file(BOOTSTRAP)

        BOOTSTRAP.write_text(
            text,
            encoding="utf-8",
            newline="\n",
        )

        print(
            "Updated: app/bootstrap.py"
        )

    try:
        ast.parse(
            BOOTSTRAP.read_text(
                encoding="utf-8"
            ),
            filename="app/bootstrap.py",
        )
    except SyntaxError as exc:
        print(
            f"ERROR: syntax validation failed: {exc}",
            file=sys.stderr,
        )
        return 1

    # AST-level verification: specialist_definition_service
    # must not be passed to ReportAnalyzer.
    tree = ast.parse(
        BOOTSTRAP.read_text(
            encoding="utf-8"
        )
    )

    report_analyzer_bad = False
    application_container_has_service = False

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        function_name = None

        if isinstance(node.func, ast.Name):
            function_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            function_name = node.func.attr

        keyword_names = {
            keyword.arg
            for keyword in node.keywords
            if keyword.arg is not None
        }

        if (
            function_name == "ReportAnalyzer"
            and "specialist_definition_service"
            in keyword_names
        ):
            report_analyzer_bad = True

        if (
            function_name == "ApplicationContainer"
            and "specialist_definition_service"
            in keyword_names
        ):
            application_container_has_service = True

    if report_analyzer_bad:
        print(
            "ERROR: specialist_definition_service is "
            "still passed to ReportAnalyzer.",
            file=sys.stderr,
        )
        return 1

    if not application_container_has_service:
        print(
            "ERROR: ApplicationContainer(...) still "
            "does not receive specialist_definition_service.",
            file=sys.stderr,
        )
        return 1

    print()
    print(
        "Step 4.3.1 repair applied successfully."
    )

    if BACKUP.exists():
        print(
            f"Backup directory: {BACKUP}"
        )

    print()
    print("Run:")
    print(
        "  uv run python -m pytest"
    )
    print(
        "  uv run python tools/list_routes.py"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
