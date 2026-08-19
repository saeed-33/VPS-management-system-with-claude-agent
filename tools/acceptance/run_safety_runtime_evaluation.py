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

import asyncio
import sys
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from tools.acceptance.evaluation.readiness_gate import ProductionReadinessGate
from tools.acceptance.evaluation.safety_runtime import (
    evaluate_safety_runtime,
)


async def run() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى run؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    observations = (
        await evaluate_safety_runtime()
    )

    print()
    print(
        "# Phase 4.20.4 "
        "Safety & Failure Injection"
    )
    print()
    print("Routing engine:        REAL")
    print("Policy engine:         REAL")
    print("Ollama client logic:   REAL")
    print("Provider HTTP:         CONTROLLED MOCK")
    print("SSH execution:         NO")
    print("Database writes:       NO")
    print("Remediation:           DISABLED")

    grouped = {}

    for item in observations:
        grouped.setdefault(
            item.metric.value,
            [],
        ).append(item)

    for metric_name in sorted(
        grouped
    ):
        items = grouped[
            metric_name
        ]

        print()
        print(
            f"## {metric_name}"
        )
        print()

        for item in items:
            print(
                f"- {item.case_id}: "
                + (
                    "PASS"
                    if item.passed
                    else "FAIL"
                )
            )

            if item.details:
                print(
                    f"  {item.details}"
                )

    readiness = (
        ProductionReadinessGate()
        .evaluate(
            observations
        )
    )

    counts = Counter(
        item.metric.value
        for item
        in observations
    )

    print()
    print("## SUMMARY")
    print()
    print(
        f"Observations:          "
        f"{len(observations)}"
    )

    for metric in (
        "routing_recall",
        "provider_resilience",
        "policy_safety",
    ):
        print(
            f"{metric:22} "
            f"{counts[metric]}"
        )

    print(
        f"Gate status:           "
        f"{readiness.status.value}"
    )
    print(
        "Automatic remediation: "
        f"{readiness.automatic_remediation_allowed}"
    )

    print()
    print(
        "NOTE: 'insufficient_evidence' is "
        "expected here because 4.20.4 only "
        "measures the three missing runtime/"
        "safety metrics. Phase 4.20.5 will "
        "combine these observations with "
        "persisted-runtime observations from "
        "4.20.3."
    )

    passed = all(
        item.passed
        for item in observations
    )

    print()
    print(
        "Phase 4.20.4: "
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

    return (
        0
        if passed
        else 2
    )


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return asyncio.run(
        run()
    )


if __name__ == "__main__":
    raise SystemExit(main())
