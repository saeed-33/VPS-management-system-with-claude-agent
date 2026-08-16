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

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str]) -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى run؛ المدخلات المهمة: command.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    print()
    print(
        "$ " + " ".join(command)
    )
    completed = subprocess.run(
        command,
        cwd=ROOT,
    )
    return completed.returncode


def tool_exists(name: str) -> bool:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى tool_exists؛ المدخلات المهمة: name.
    تعيد bool أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return (
        ROOT
        / "tools"
        / name
    ).exists()


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run the documented chat_system "
            "test/evaluation sequence."
        )
    )
    parser.add_argument(
        "--mode",
        choices=(
            "quick",
            "full",
            "readiness",
        ),
        default="full",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
    )
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
    )
    args = parser.parse_args()

    commands = [
        [
            sys.executable,
            "-m",
            "pytest",
        ],
    ]

    if args.mode in {
        "full",
        "readiness",
    }:
        optional = (
            (
                "list_routes.py",
                [
                    sys.executable,
                    "tools/dev/list_routes.py",
                ],
            ),
            (
                "run_evaluation_dataset.py",
                [
                    sys.executable,
                    "tools/acceptance/run_evaluation_dataset.py",
                ],
            ),
            (
                "run_safety_runtime_evaluation.py",
                [
                    sys.executable,
                    "tools/acceptance/run_safety_runtime_evaluation.py",
                ],
            ),
        )

        for filename, command in optional:
            if tool_exists(filename):
                commands.append(command)

    if args.mode == "readiness":
        optional = (
            (
                "run_persisted_runtime_evaluation.py",
                [
                    sys.executable,
                    "tools/acceptance/run_persisted_runtime_evaluation.py",
                    "--limit",
                    str(args.limit),
                ],
            ),
            (
                "run_production_readiness_evaluation.py",
                [
                    sys.executable,
                    "tools/acceptance/run_production_readiness_evaluation.py",
                    "--limit",
                    str(args.limit),
                ],
            ),
        )

        for filename, command in optional:
            if tool_exists(filename):
                commands.append(command)

    failures = []

    for command in commands:
        code = run(command)

        if code != 0:
            failures.append(
                (
                    command,
                    code,
                )
            )

            if not args.continue_on_failure:
                break

    print()
    print(
        f"Commands executed: "
        f"{len(commands)}"
    )
    print(
        f"Failures: "
        f"{len(failures)}"
    )

    if failures:
        for command, code in failures:
            print(
                f"- {code}: "
                + " ".join(command)
            )

    return (
        0
        if not failures
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
