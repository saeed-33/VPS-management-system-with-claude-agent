"""Check local Markdown links in the consolidated documentation."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[2]
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    bad: list[tuple[str, str]] = []
    for path in (ROOT / "docs").rglob("*.md"):
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            target = target.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if target.startswith("/"):
                candidate = ROOT / target.lstrip("/")
            else:
                candidate = path.parent / unquote(urlsplit(target).path)
            if candidate.suffix and not candidate.exists():
                bad.append((path.relative_to(ROOT).as_posix(), target))
    if bad:
        for path, target in bad[:50]:
            print(f"BROKEN {path}: {target}")
        return 1
    print("DOCUMENTATION_LINKS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
