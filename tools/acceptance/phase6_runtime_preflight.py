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

import os
import shutil
import subprocess
import sys
from pathlib import Path


REQUIRED_SUPPORTED_FLAGS = ("--settings", "--mcp-config", "--strict-mcp-config", "--add-dir")


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    executable = os.getenv("CLAUDE_RUNTIME_EXECUTABLE", "claude")
    path = shutil.which(executable)
    if path is None:
        print("PHASE6_SANDBOX_RUNTIME=BLOCKED_BY_SANDBOX_RUNTIME: Claude executable unavailable")
        return 1
    result = subprocess.run([path, "--help"], capture_output=True, text=True, check=False)
    missing = [flag for flag in REQUIRED_SUPPORTED_FLAGS if flag not in result.stdout]
    if missing:
        print("PHASE6_SANDBOX_RUNTIME=BLOCKED_BY_SANDBOX_RUNTIME: unsupported CLI flags: " + ", ".join(missing))
        return 1
    print("PHASE6_SANDBOX_RUNTIME=SUPPORTED_CLI_SURFACE")
    print("Use --settings .claude/settings.json --mcp-config .mcp.json --strict-mcp-config --add-dir <project>.")
    print("Native sandbox acceptance still requires an attestation produced from inside the sandbox.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
