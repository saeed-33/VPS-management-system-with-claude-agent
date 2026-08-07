from __future__ import annotations

from datetime import datetime
from pathlib import Path
import ast
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parent
BOOTSTRAP = ROOT / "app" / "bootstrap.py"
BACKUP = (
    ROOT
    / ".step_4_3_2_backup"
    / datetime.now().strftime("%Y%m%d_%H%M%S")
)


def backup_file(path: Path) -> None:
    destination = BACKUP / path.relative_to(ROOT)
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    shutil.copy2(path, destination)


def find_call_span(
    text: str,
    call_name: str,
) -> tuple[int, int]:
    marker = f"{call_name}("
    start = text.find(marker)

    if start == -1:
        raise RuntimeError(
            f"{call_name}(...) was not found."
        )

    open_index = start + len(call_name)

    depth = 0
    quote: str | None = None
    triple = False
    escaped = False
    i = open_index

    while i < len(text):
        char = text[i]

        if quote is not None:
            if escaped:
                escaped = False
                i += 1
                continue

            if char == "\\":
                escaped = True
                i += 1
                continue

            if triple:
                if text.startswith(
                    quote * 3,
                    i,
                ):
                    quote = None
                    triple = False
                    i += 3
                    continue
            elif char == quote:
                quote = None

            i += 1
            continue

        if char in {"'", '"'}:
            if text.startswith(
                char * 3,
                i,
            ):
                quote = char
                triple = True
                i += 3
            else:
                quote = char
                i += 1
            continue

        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1

            if depth == 0:
                return start, i + 1

        i += 1

    raise RuntimeError(
        f"Could not find closing parenthesis for "
        f"{call_name}(...)."
    )


def remove_specialist_keyword_from_call(
    call_text: str,
) -> tuple[str, int]:
    patterns = [
        # Multi-line parenthesized value.
        re.compile(
            r"""
            \n[ \t]*
            specialist_definition_service
            [ \t]*=[ \t]*\(
            [ \t\r\n]*
            specialist_definition_service
            [ \t\r\n]*
            \)
            [ \t]*,
            """,
            re.VERBOSE,
        ),
        # Direct value form.
        re.compile(
            r"""
            \n[ \t]*
            specialist_definition_service
            [ \t]*=[ \t]*
            specialist_definition_service
            [ \t]*,
            """,
            re.VERBOSE,
        ),
    ]

    total = 0
    result = call_text

    for pattern in patterns:
        result, count = pattern.subn(
            "",
            result,
        )
        total += count

    return result, total


def verify_ast(text: str) -> None:
    tree = ast.parse(
        text,
        filename="app/bootstrap.py",
    )

    report_calls = []
    container_calls = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(
            node.func,
            ast.Attribute,
        ):
            name = node.func.attr
        else:
            continue

        keywords = {
            keyword.arg
            for keyword in node.keywords
            if keyword.arg is not None
        }

        if name == "ReportAnalyzer":
            report_calls.append(keywords)

        if name == "ApplicationContainer":
            container_calls.append(keywords)

    if not report_calls:
        raise RuntimeError(
            "No ReportAnalyzer(...) call found "
            "during AST verification."
        )

    if any(
        "specialist_definition_service"
        in keywords
        for keywords in report_calls
    ):
        raise RuntimeError(
            "specialist_definition_service is still "
            "passed to ReportAnalyzer(...)."
        )

    if not container_calls:
        raise RuntimeError(
            "No ApplicationContainer(...) call found."
        )

    if not any(
        "specialist_definition_service"
        in keywords
        for keywords in container_calls
    ):
        raise RuntimeError(
            "ApplicationContainer(...) does not receive "
            "specialist_definition_service."
        )


def main() -> int:
    if not (
        ROOT / "app" / "main.py"
    ).exists():
        print(
            "ERROR: run from project root.",
            file=sys.stderr,
        )
        return 1

    if not BOOTSTRAP.exists():
        print(
            "ERROR: app/bootstrap.py not found.",
            file=sys.stderr,
        )
        return 1

    text = BOOTSTRAP.read_text(
        encoding="utf-8"
    )

    try:
        start, end = find_call_span(
            text,
            "ReportAnalyzer",
        )

        call_text = text[start:end]

        fixed_call, removed = (
            remove_specialist_keyword_from_call(
                call_text
            )
        )

        if removed == 0:
            print(
                "No textual specialist keyword was "
                "removed from ReportAnalyzer; "
                "AST verification will determine state."
            )
        else:
            text = (
                text[:start]
                + fixed_call
                + text[end:]
            )

            print(
                "Removed "
                f"{removed} invalid "
                "specialist_definition_service "
                "argument(s) from ReportAnalyzer(...)."
            )

        # Ensure ApplicationContainer receives the service.
        container_start, container_end = (
            find_call_span(
                text,
                "ApplicationContainer",
            )
        )

        container_call = text[
            container_start:container_end
        ]

        if (
            "specialist_definition_service="
            not in container_call
        ):
            marker = (
                "        report_query_service="
                "report_query_service,\n"
            )

            addition = marker + (
                "        specialist_definition_service=(\n"
                "            specialist_definition_service\n"
                "        ),\n"
            )

            if marker not in container_call:
                raise RuntimeError(
                    "Could not locate report_query_service "
                    "inside ApplicationContainer(...)."
                )

            container_call = (
                container_call.replace(
                    marker,
                    addition,
                    1,
                )
            )

            text = (
                text[:container_start]
                + container_call
                + text[container_end:]
            )

            print(
                "Added specialist_definition_service "
                "to ApplicationContainer(...)."
            )
        else:
            print(
                "ApplicationContainer already receives "
                "specialist_definition_service."
            )

        # Verify the dataclass and construction exist.
        if (
            "specialist_definition_service: "
            "SpecialistDefinitionService"
            not in text
        ):
            raise RuntimeError(
                "ApplicationContainer dataclass field "
                "specialist_definition_service is missing."
            )

        if (
            "specialist_definition_service = ("
            not in text
            or "SpecialistDefinitionService("
            not in text
        ):
            raise RuntimeError(
                "SpecialistDefinitionService construction "
                "is missing from build_container()."
            )

        verify_ast(text)

    except Exception as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 1

    current = BOOTSTRAP.read_text(
        encoding="utf-8"
    )

    if current != text:
        backup_file(BOOTSTRAP)
        BOOTSTRAP.write_text(
            text,
            encoding="utf-8",
            newline="\n",
        )
        print(
            "Updated: app/bootstrap.py"
        )
    else:
        print(
            "No file changes required."
        )

    # Verify the written file one final time.
    try:
        verify_ast(
            BOOTSTRAP.read_text(
                encoding="utf-8"
            )
        )
    except Exception as exc:
        print(
            f"ERROR after write: {exc}",
            file=sys.stderr,
        )
        return 1

    print()
    print(
        "Step 4.3.2 repair applied successfully."
    )

    if BACKUP.exists():
        print(
            f"Backup directory: {BACKUP}"
        )

    print()
    print("Run:")
    print(
        "  uv run python tools/list_routes.py"
    )
    print(
        "  uv run python -m pytest"
    )
    print(
        "  uv run python -m uvicorn "
        "app.main:app --reload"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
