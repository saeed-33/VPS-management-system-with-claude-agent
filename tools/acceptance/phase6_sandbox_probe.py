"""
مشغل acceptance/evaluation ينفذ سيناريوهات readiness أو safety ويجمع نتائج قابلة للمراجعة.

الموقع في المعمارية: Acceptance tooling.
يُستدعى بواسطة: المشغل اليدوي أو CI.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يغير policy الإنتاجية؛ ينفذ evaluation خارج runtime المعتاد.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


def _sensitive_path_is_inaccessible(raw_path: str) -> bool:
    """
    Verify that a configured sensitive path cannot be read.

    Path metadata may remain visible inside a sandbox, so Path.exists()
    alone is not a valid read-isolation check.
    """
    path = Path(raw_path)

    try:
        with path.open("rb") as handle:
            handle.read(1)
    except (PermissionError, FileNotFoundError):
        return True
    except IsADirectoryError:
        try:
            next(path.iterdir(), None)
        except (PermissionError, FileNotFoundError):
            return True
        return False

    return False


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    project_root = Path(
        os.getenv("CLAUDE_PROJECT_DIR", Path.cwd())
    ).resolve()
    cwd = Path.cwd().resolve()

    sandbox_marker = (
        os.getenv("PHASE6_NATIVE_SANDBOX", "")
        .strip()
        .lower()
        == "true"
    )

    sensitive_paths = [
        item
        for item in os.getenv(
            "PHASE6_SENSITIVE_PATHS",
            "",
        ).split(os.pathsep)
        if item
    ]

    sensitive_path_checks = {
        item: _sensitive_path_is_inaccessible(item)
        for item in sensitive_paths
    }

    # Fail closed: no configured sensitive path is not evidence.
    sensitive_inaccessible = (
        bool(sensitive_paths)
        and all(sensitive_path_checks.values())
    )

    payload = {
        "sandboxed": sandbox_marker,
        "project_path_accessible": (
            cwd == project_root
            or project_root in cwd.parents
        ),
        "sensitive_path_inaccessible": sensitive_inaccessible,
        "unsandboxed_escape_unavailable": (
            os.getenv(
                "PHASE6_UNSANDBOXED_ESCAPE_DENIED",
                "",
            )
            .strip()
            .lower()
            == "true"
        ),
        "sensitive_path_checks": sensitive_path_checks,
        "cwd": str(cwd),
        "project_root": str(project_root),
        "runtime": "claude-native-sandbox",
    }

    output = os.getenv(
        "PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE",
        "",
    ).strip()

    if output:
        Path(output).write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )

    print(json.dumps(payload, indent=2))

    required = (
        "sandboxed",
        "project_path_accessible",
        "sensitive_path_inaccessible",
        "unsandboxed_escape_unavailable",
    )

    return 0 if all(payload[key] for key in required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
