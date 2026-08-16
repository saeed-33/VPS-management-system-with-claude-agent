"""
أداة CLI لإدارة database أو تشغيل MCP أو سيناريو خارجي.

الموقع في المعمارية: Operational tooling.
يُستدعى بواسطة: مشغل الأداة أو deployment workflow.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف endpoint أو capability تلقائيًا إلى التطبيق.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SCENARIOS = (
    "cpu",
    "memory",
    "disk-io",
    "process-churn",
    "tcp-listener",
    "http-local",
    "mixed",
)


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run a deterministic matrix of "
            "safe Linux workload scenarios."
        )
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=8.0,
    )
    parser.add_argument(
        "--output",
        default=(
            "linux-scenario-matrix.json"
        ),
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
    )
    args = parser.parse_args()

    script = (
        Path(__file__).with_name(
            "random_linux_workload.py"
        )
    )

    results = []

    for index, scenario in enumerate(
        SCENARIOS,
        start=1,
    ):
        command = [
            sys.executable,
            str(script),
            "--scenario",
            scenario,
            "--seed",
            str(
                args.seed + index
            ),
            "--duration",
            str(args.duration),
        ]

        print(
            f"[{index}/{len(SCENARIOS)}] "
            f"{scenario}"
        )

        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
        )

        record = {
            "scenario": scenario,
            "seed": (
                args.seed + index
            ),
            "returncode": (
                completed.returncode
            ),
            "stdout": (
                completed.stdout
            ),
            "stderr": (
                completed.stderr
            ),
        }

        results.append(record)

        if (
            completed.returncode != 0
            and args.stop_on_failure
        ):
            break

    payload = {
        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "base_seed": args.seed,
        "duration": args.duration,
        "results": results,
    }

    output = Path(args.output)
    output.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    failures = sum(
        1
        for item in results
        if item["returncode"] != 0
    )

    print()
    print(
        f"Scenarios executed: "
        f"{len(results)}"
    )
    print(
        f"Failures: {failures}"
    )
    print(
        f"Report: {output}"
    )

    return (
        0
        if failures == 0
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
