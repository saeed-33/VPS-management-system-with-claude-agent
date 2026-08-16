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

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

BEGIN = "<!-- PROJECT-DOC-METADATA:BEGIN -->"
END = "<!-- PROJECT-DOC-METADATA:END -->"

STALE_CURRENT_PATTERNS = (
    "Implemented through **Phase 4.17**",
    "Implemented baseline through Phase 4.17",
    "Phase 4.17 is accepted",
    "The next workflow is Phase 4.18",
    "## Phase 4.18 target",
    "| 4.18 | Next",
    "| 4.19 | Planned",
    "| 4.20 | Planned",
    "Current: **4.18",
)

HISTORICAL = {
    "docs/roadmap/phase-4-17-closeout.md",
    "docs/roadmap/phase-4-18-implementation.md",
    "docs/roadmap/phase-4-19-implementation.md",
    "docs/roadmap/phase-4-4-5-to-4-11-closeout.md",
    "docs/roadmap/phase-4-foundation-closeout.md",
}


def rel(path: Path) -> str:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى rel؛ المدخلات المهمة: path.
    تعيد str أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return path.relative_to(ROOT).as_posix()


def local_markdown_links(
    path: Path,
    text: str,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى local_markdown_links؛ المدخلات المهمة: path، text.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    pattern = re.compile(
        r"\[[^\]]+\]\(([^)]+)\)"
    )

    for target in pattern.findall(text):
        target = target.strip()

        if not target:
            continue

        if target.startswith(
            (
                "http://",
                "https://",
                "mailto:",
                "#",
            )
        ):
            continue

        target = target.split("#", 1)[0]

        if not target:
            continue

        if target.startswith("/"):
            candidate = (
                ROOT
                / target.lstrip("/")
            )
        else:
            candidate = (
                path.parent
                / target
            ).resolve()

        yield target, candidate


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    errors = []

    docs = sorted(
        DOCS.rglob("*.md")
    )

    for path in docs:
        text = path.read_text(
            encoding="utf-8"
        )

        name = rel(path)

        if BEGIN not in text or END not in text:
            errors.append(
                f"{name}: missing managed metadata block"
            )

        if name not in HISTORICAL:
            for stale in STALE_CURRENT_PATTERNS:
                if stale in text:
                    errors.append(
                        f"{name}: stale current-state phrase: {stale!r}"
                    )

        for target, candidate in local_markdown_links(
            path,
            text,
        ):
            if not candidate.exists():
                errors.append(
                    f"{name}: broken local link {target!r}"
                )

    status = DOCS / "PROJECT_STATUS.md"

    if not status.exists():
        errors.append(
            "docs/PROJECT_STATUS.md missing"
        )
    else:
        text = status.read_text(
            encoding="utf-8"
        )
        if (
            "ready_for_supervised_operations"
            not in text
        ):
            errors.append(
                "PROJECT_STATUS missing readiness state"
            )
        if (
            "automatic_remediation_allowed: false"
            not in text
        ):
            errors.append(
                "PROJECT_STATUS missing remediation boundary"
            )

    inventory = (
        DOCS
        / "DOCUMENTATION_INVENTORY.md"
    )

    if not inventory.exists():
        errors.append(
            "DOCUMENTATION_INVENTORY.md missing"
        )

    print(
        f"Documentation files audited: "
        f"{len(docs)}"
    )

    if errors:
        print()
        print("Documentation audit: FAIL")

        for error in errors:
            print(
                f"- {error}"
            )

        return 2

    print(
        "Documentation audit: PASS"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
