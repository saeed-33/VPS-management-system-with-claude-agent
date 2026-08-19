"""Tests for test production readiness.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from tools.acceptance.evaluation.readiness_gate import DEFAULT_THRESHOLDS, ProductionReadinessGate
from tools.acceptance.evaluation.contracts import EvaluationMetric, EvaluationObservation, MetricThreshold, ReadinessStatus


def observations_for_thresholds(
    *,
    fail_metric=None,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى observations_for_thresholds؛ المدخلات المهمة: fail_metric.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    items = []

    for threshold in DEFAULT_THRESHOLDS:
        for index in range(
            threshold.minimum_samples
        ):
            passed = not (
                threshold.metric
                == fail_metric
                and index == 0
            )

            items.append(
                EvaluationObservation(
                    case_id=(
                        f"{threshold.metric.value}:"
                        f"{index + 1}"
                    ),
                    metric=threshold.metric,
                    passed=passed,
                )
            )

    return tuple(items)


def test_gate_requires_minimum_samples():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_gate_requires_minimum_samples؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    gate = ProductionReadinessGate()

    result = gate.evaluate(())

    assert (
        result.status
        == ReadinessStatus.INSUFFICIENT_EVIDENCE
    )

    assert (
        result.automatic_remediation_allowed
        is False
    )

    assert result.blocking_reasons


def test_all_thresholds_pass_supervised_only():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_all_thresholds_pass_supervised_only؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    gate = ProductionReadinessGate()

    result = gate.evaluate(
        observations_for_thresholds()
    )

    assert (
        result.status
        == ReadinessStatus
        .READY_FOR_SUPERVISED_OPERATIONS
    )

    assert (
        result.automatic_remediation_allowed
        is False
    )

    assert result.blocking_reasons == ()


def test_hard_safety_failure_blocks():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_hard_safety_failure_blocks؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    gate = ProductionReadinessGate()

    result = gate.evaluate(
        observations_for_thresholds(
            fail_metric=(
                EvaluationMetric
                .EVIDENCE_GROUNDING
            )
        )
    )

    assert (
        result.status
        == ReadinessStatus.BLOCKED
    )

    assert any(
        "hard safety failure"
        in item
        for item
        in result.blocking_reasons
    )


def test_policy_failure_blocks():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_policy_failure_blocks؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    gate = ProductionReadinessGate()

    result = gate.evaluate(
        observations_for_thresholds(
            fail_metric=(
                EvaluationMetric
                .POLICY_SAFETY
            )
        )
    )

    assert (
        result.status
        == ReadinessStatus.BLOCKED
    )


def test_soft_metric_can_fail_rate_threshold():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_soft_metric_can_fail_rate_threshold؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    threshold = MetricThreshold(
        metric=EvaluationMetric.ROUTING_RECALL,
        minimum_pass_rate=0.8,
        minimum_samples=5,
    )

    gate = ProductionReadinessGate(
        thresholds=(threshold,)
    )

    observations = tuple(
        EvaluationObservation(
            case_id=f"case-{index}",
            metric=(
                EvaluationMetric.ROUTING_RECALL
            ),
            passed=index < 3,
        )
        for index in range(5)
    )

    result = gate.evaluate(
        observations
    )

    assert (
        result.status
        == ReadinessStatus.BLOCKED
    )

    assert (
        result.metrics[0].pass_rate
        == 0.6
    )


def test_duplicate_thresholds_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_duplicate_thresholds_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    threshold = MetricThreshold(
        metric=EvaluationMetric.ROUTING_RECALL,
        minimum_pass_rate=1.0,
        minimum_samples=1,
    )

    try:
        ProductionReadinessGate(
            thresholds=(
                threshold,
                threshold,
            )
        )
    except ValueError as exc:
        assert (
            "Duplicate metric thresholds"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Duplicate thresholds accepted."
        )
