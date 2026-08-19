"""Tests for test runtime readiness gate.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from tools.acceptance.evaluation.contracts import EvaluationMetric, EvaluationObservation, ReadinessStatus
from tools.acceptance.evaluation.runtime_readiness import RUNTIME_READINESS_CASES, RuntimeReadinessGate


CRITICAL_SAMPLE_METRICS = (
    EvaluationMetric.EVIDENCE_GROUNDING,
    EvaluationMetric.POLICY_SAFETY,
    EvaluationMetric.FIXED_WORKFLOW_PRESERVATION,
    EvaluationMetric.SANDBOX_VALIDATION_BEHAVIOR,
)


def observations(
    *,
    fail_case=None,
    fail_metric=None,
    omit_case=None,
    score_drop_case=None,
    score_drop_metric=None,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى observations؛ المدخلات المهمة: fail_case، fail_metric، omit_case، score_drop_case، score_drop_metric.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    items = []
    for case_id in RUNTIME_READINESS_CASES:
        if case_id == omit_case:
            continue
        for metric in CRITICAL_SAMPLE_METRICS:
            passed = not (
                case_id == fail_case
                and metric == fail_metric
            )
            score = 1.0
            if (
                case_id == score_drop_case
                and metric == score_drop_metric
            ):
                score = 0.5
            items.append(
                EvaluationObservation(
                    case_id=case_id,
                    metric=metric,
                    passed=passed,
                    score=score,
                )
            )
    return tuple(items)


def test_runtime_readiness_gate_passes_full_non_regressing_matrix():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_readiness_gate_passes_full_non_regressing_matrix؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = RuntimeReadinessGate().evaluate(
        reference_observations=observations(),
        runtime_observations=observations(),
    )

    assert (
        result.status
        == ReadinessStatus
        .READY_FOR_SUPERVISED_OPERATIONS
    )
    assert result.runtime_ready is True
    assert (
        result.automatic_remediation_allowed
        is False
    )
    assert result.blocking_reasons == ()


def test_runtime_readiness_gate_blocks_missing_runtime_case():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_readiness_gate_blocks_missing_runtime_case؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = RuntimeReadinessGate().evaluate(
        reference_observations=observations(),
        runtime_observations=observations(
            omit_case="disk-issue"
        ),
    )

    assert (
        result.status
        == ReadinessStatus.INSUFFICIENT_EVIDENCE
    )
    assert result.runtime_ready is False
    assert any(
        "disk-issue" in item
        for item in result.blocking_reasons
    )


def test_runtime_readiness_gate_blocks_critical_regression():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_readiness_gate_blocks_critical_regression؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = RuntimeReadinessGate().evaluate(
        reference_observations=observations(),
        runtime_observations=observations(
            fail_case="tool-denied",
            fail_metric=(
                EvaluationMetric.POLICY_SAFETY
            ),
        ),
    )

    assert result.status == ReadinessStatus.BLOCKED
    assert result.runtime_ready is False
    assert any(
        "tool-denied/policy_safety"
        in item
        for item in result.blocking_reasons
    )


def test_runtime_readiness_gate_blocks_critical_score_regression():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_readiness_gate_blocks_critical_score_regression؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = RuntimeReadinessGate().evaluate(
        reference_observations=observations(),
        runtime_observations=observations(
            score_drop_case=(
                "sandbox-remediation-failure"
            ),
            score_drop_metric=(
                EvaluationMetric
                .SANDBOX_VALIDATION_BEHAVIOR
            ),
        ),
    )

    assert result.status == ReadinessStatus.BLOCKED
    assert any(
        comparison.material_regression
        for comparison in result.comparisons
        if comparison.case_id
        == "sandbox-remediation-failure"
    )


def test_non_critical_regression_is_recorded_but_does_not_block():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_non_critical_regression_is_recorded_but_does_not_block؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    reference = observations() + (
        EvaluationObservation(
            case_id="high-cpu",
            metric=EvaluationMetric.LATENCY,
            passed=True,
            score=1.0,
        ),
    )
    runtime = observations() + (
        EvaluationObservation(
            case_id="high-cpu",
            metric=EvaluationMetric.LATENCY,
            passed=False,
            score=0.1,
        ),
    )

    result = RuntimeReadinessGate().evaluate(
        reference_observations=reference,
        runtime_observations=runtime,
    )

    assert (
        result.status
        == ReadinessStatus
        .READY_FOR_SUPERVISED_OPERATIONS
    )
    assert any(
        comparison.material_regression
        and not comparison.critical
        for comparison in result.comparisons
    )


def test_duplicate_observations_are_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_duplicate_observations_are_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    duplicate = observations() + (
        EvaluationObservation(
            case_id="high-cpu",
            metric=(
                EvaluationMetric
                .EVIDENCE_GROUNDING
            ),
            passed=True,
        ),
    )

    try:
        RuntimeReadinessGate().evaluate(
            reference_observations=duplicate,
            runtime_observations=observations(),
        )
    except ValueError as exc:
        assert (
            "Duplicate observation"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Duplicate observations accepted."
        )
