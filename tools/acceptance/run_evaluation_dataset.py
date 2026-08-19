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

import sys
from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from tools.acceptance.evaluation.runner import DeterministicEvaluationRunner, expected_behavior_executor
from tools.acceptance.evaluation.cases import default_evaluation_cases

def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Acceptance tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    cases = default_evaluation_cases()

    result = (
        DeterministicEvaluationRunner()
        .run(
            cases=cases,
            executor=(
                expected_behavior_executor
            ),
        )
    )

    category_counts = Counter(
        case.category
        for case in cases
    )

    print()
    print(
        "# Phase 4.20.2 "
        "Evaluation Dataset Validation"
    )
    print()
    print(
        f"Cases:              "
        f"{result.cases_total}"
    )
    print(
        f"Expected passes:    "
        f"{result.cases_passed}"
    )
    print(
        f"Observations:       "
        f"{len(result.observations)}"
    )
    print(
        f"Gate status:        "
        f"{result.readiness.status.value}"
    )
    print(
    "Automatic repair:   "
    f"{result.readiness.automatic_remediation_allowed}"
    )

    print()
    print("## CASE CATEGORIES")
    print()

    for category in sorted(
        category_counts
    ):
        print(
            f"- {category}: "
            f"{category_counts[category]}"
        )

    print()
    print("## METRIC COVERAGE")
    print()

    for metric in (
        result.readiness.metrics
    ):
        print(
            f"- {metric.metric.value}: "
            f"{metric.samples} samples "
            f"(required "
            f"{metric.required_samples})"
        )

    print()
    print(
        "NOTE: This validates dataset "
        "coverage and gate wiring only."
    )
    print(
        "It is NOT a runtime quality score."
    )
    print(
        "Phase 4.20.3 will execute "
        "runtime-backed evaluation cases."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
