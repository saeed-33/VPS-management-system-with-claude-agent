"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio

from tools.acceptance.evaluation.contracts import (
    EvaluationMetric,
)
from tools.acceptance.evaluation.safety_runtime import (
    evaluate_policy_cases,
    evaluate_provider_cases,
    evaluate_routing_cases,
)


def test_routing_runtime_emits_ten_passes():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_routing_runtime_emits_ten_passes؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    items = evaluate_routing_cases()

    assert len(items) == 10
    assert all(
        item.metric
        == EvaluationMetric.ROUTING_RECALL
        for item in items
    )
    assert all(
        item.passed
        for item in items
    )


def test_policy_runtime_emits_ten_passes():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_policy_runtime_emits_ten_passes؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    items = evaluate_policy_cases()

    assert len(items) == 10
    assert all(
        item.metric
        == EvaluationMetric.POLICY_SAFETY
        for item in items
    )
    assert all(
        item.passed
        for item in items
    )


def test_provider_runtime_emits_ten_safe_results():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_provider_runtime_emits_ten_safe_results؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    items = asyncio.run(
        evaluate_provider_cases()
    )

    assert len(items) == 10
    assert all(
        item.metric
        == EvaluationMetric.PROVIDER_RESILIENCE
        for item in items
    )
    assert all(
        item.passed
        for item in items
    )
