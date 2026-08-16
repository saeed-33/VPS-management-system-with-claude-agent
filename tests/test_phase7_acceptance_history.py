"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from types import SimpleNamespace

from tests.real_runtime.test_phase7_real_autonomous_acceptance import (
    _assert_candidate_delta,
    _assert_history_delta,
)


def test_acceptance_history_delta_requires_three_new_clean_successes():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_acceptance_history_delta_requires_three_new_clean_successes؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    baseline = SimpleNamespace(
        supervised_execution_count=3,
        successful_execution_count=3,
        verified_success_count=3,
        failed_execution_count=1,
        verification_failure_count=0,
        rollback_failure_count=0,
    )
    current = SimpleNamespace(
        supervised_execution_count=6,
        successful_execution_count=6,
        verified_success_count=6,
        failed_execution_count=1,
        verification_failure_count=0,
        rollback_failure_count=0,
    )

    _assert_history_delta(baseline, current)


def test_acceptance_candidate_delta_allows_legitimate_prior_history():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_acceptance_candidate_delta_allows_legitimate_prior_history؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    baseline = SimpleNamespace(
        execution_count=3,
        verified_success_count=3,
        failure_count=0,
        rollback_failure_count=0,
    )
    current = SimpleNamespace(
        execution_count=6,
        verified_success_count=6,
        failure_count=0,
        rollback_failure_count=0,
        success_rate=1.0,
    )

    _assert_candidate_delta(baseline, current)
