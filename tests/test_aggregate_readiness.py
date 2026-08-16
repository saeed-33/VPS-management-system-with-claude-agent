"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from tools.acceptance.evaluation.aggregate_readiness import (
    AggregateReadinessEvaluator,
)
from tools.acceptance.evaluation.contracts import (
    EvaluationMetric,
    EvaluationObservation,
    ReadinessStatus,
)


def obs(
    case_id,
    metric,
    *,
    passed=True,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى obs؛ المدخلات المهمة: case_id، metric، passed.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return EvaluationObservation(
        case_id=case_id,
        metric=metric,
        passed=passed,
        score=1.0 if passed else 0.0,
    )


def test_aggregate_combines_sources():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_aggregate_combines_sources؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    persisted = (
        obs(
            "p1",
            EvaluationMetric
            .SPECIALIST_COMPLETION,
        ),
    )

    safety = (
        obs(
            "s1",
            EvaluationMetric
            .ROUTING_RECALL,
        ),
    )

    result = (
        AggregateReadinessEvaluator()
        .evaluate(
            persisted_observations=(
                persisted
            ),
            safety_observations=safety,
        )
    )

    assert len(
        result.observations
    ) == 2


def test_sample_deficits_are_reported():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_sample_deficits_are_reported؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = (
        AggregateReadinessEvaluator()
        .evaluate(
            persisted_observations=(
                obs(
                    "p1",
                    EvaluationMetric
                    .EVIDENCE_GROUNDING,
                ),
            ),
            safety_observations=(),
        )
    )

    assert (
        result.sample_deficits[
            EvaluationMetric
            .EVIDENCE_GROUNDING
        ]
        == 9
    )


def test_one_real_runtime_sample_is_not_ready():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_one_real_runtime_sample_is_not_ready؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    persisted = tuple(
        obs(
            f"p-{metric.value}",
            metric,
        )
        for metric in (
            EvaluationMetric
            .SPECIALIST_COMPLETION,
            EvaluationMetric
            .EVIDENCE_GROUNDING,
            EvaluationMetric
            .BUDGET_COMPLIANCE,
            EvaluationMetric
            .CONFLICT_PRESERVATION,
            EvaluationMetric
            .FINAL_DIAGNOSIS_GROUNDING,
        )
    )

    safety = tuple(
        obs(
            f"s-{metric.value}-{index}",
            metric,
        )
        for metric in (
            EvaluationMetric.ROUTING_RECALL,
            EvaluationMetric
            .PROVIDER_RESILIENCE,
            EvaluationMetric.POLICY_SAFETY,
        )
        for index in range(10)
    )

    result = (
        AggregateReadinessEvaluator()
        .evaluate(
            persisted_observations=(
                persisted
            ),
            safety_observations=safety,
        )
    )

    assert (
        result.readiness.status
        == ReadinessStatus
        .INSUFFICIENT_EVIDENCE
    )

    assert (
        result.readiness
        .automatic_remediation_allowed
        is False
    )


def test_hard_failure_blocks_when_samples_sufficient():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_hard_failure_blocks_when_samples_sufficient؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    persisted = []

    for metric, count in (
        (
            EvaluationMetric
            .SPECIALIST_COMPLETION,
            10,
        ),
        (
            EvaluationMetric
            .EVIDENCE_GROUNDING,
            10,
        ),
        (
            EvaluationMetric
            .BUDGET_COMPLIANCE,
            10,
        ),
        (
            EvaluationMetric
            .CONFLICT_PRESERVATION,
            5,
        ),
        (
            EvaluationMetric
            .FINAL_DIAGNOSIS_GROUNDING,
            10,
        ),
    ):
        for index in range(count):
            persisted.append(
                obs(
                    f"{metric.value}-{index}",
                    metric,
                    passed=not (
                        metric
                        == EvaluationMetric
                        .EVIDENCE_GROUNDING
                        and index == 0
                    ),
                )
            )

    safety = tuple(
        obs(
            f"{metric.value}-{index}",
            metric,
        )
        for metric in (
            EvaluationMetric.ROUTING_RECALL,
            EvaluationMetric
            .PROVIDER_RESILIENCE,
            EvaluationMetric.POLICY_SAFETY,
        )
        for index in range(10)
    )

    result = (
        AggregateReadinessEvaluator()
        .evaluate(
            persisted_observations=tuple(
                persisted
            ),
            safety_observations=safety,
        )
    )

    assert (
        result.readiness.status
        == ReadinessStatus.BLOCKED
    )
