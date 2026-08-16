"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from tools.acceptance.evaluation.phase5_readiness import (
    Phase5Metric,
    Phase5Observation,
    Phase5ReadinessGate,
)


def test_phase5_gate_requires_all_metrics_and_real_acceptance():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_phase5_gate_requires_all_metrics_and_real_acceptance؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    observations = [Phase5Observation(metric, 1, 1) for metric in Phase5Metric]
    blocked = Phase5ReadinessGate().evaluate(
        observations,
        real_acceptance_status="BLOCKED_BY_SAFE_TEST_ENVIRONMENT",
    )
    assert blocked.status == "BLOCKED"
    assert any("safe test environment" in reason for reason in blocked.blocking_reasons)
    assert blocked.automatic_remediation_allowed is False


def test_phase5_gate_passes_only_with_explicit_real_acceptance():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_phase5_gate_passes_only_with_explicit_real_acceptance؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    observations = [Phase5Observation(metric, 1, 1) for metric in Phase5Metric]
    ready = Phase5ReadinessGate().evaluate(observations, real_acceptance_status="PASS")
    assert ready.status == "READY_FOR_SUPERVISED_OPERATIONS"
    assert all(metric.passed for metric in ready.metrics)
