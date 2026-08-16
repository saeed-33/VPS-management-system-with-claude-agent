"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.analysis.retrieval.reuse_policy.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import pytest

from app.capabilities.analysis.retrieval.reuse_policy import (
    AnalysisDecision,
    AnalysisReusePolicy,
)


@pytest.fixture
def policy() -> AnalysisReusePolicy:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى policy؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد AnalysisReusePolicy أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return AnalysisReusePolicy()


def test_exact_fingerprint_reuses_analysis(policy):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_exact_fingerprint_reuses_analysis؛ المدخلات المهمة: policy.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = policy.decide(
        fingerprint_match=True,
        historical_context_available=False,
        assisted_enabled=True,
    )

    assert result.decision == AnalysisDecision.REUSE
    assert result.reason == "exact_fingerprint_match"


def test_force_always_requires_full_analysis(policy):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_force_always_requires_full_analysis؛ المدخلات المهمة: policy.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = policy.decide(
        fingerprint_match=True,
        historical_context_available=True,
        assisted_enabled=True,
        force=True,
    )

    assert result.decision == AnalysisDecision.FULL
    assert result.reason == "forced_analysis"


def test_compatible_historical_context_is_assisted(policy):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_compatible_historical_context_is_assisted؛ المدخلات المهمة: policy.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = policy.decide(
        fingerprint_match=False,
        historical_context_available=True,
        assisted_enabled=True,
    )

    assert result.decision == AnalysisDecision.ASSISTED


def test_context_is_ignored_when_assisted_is_disabled(policy):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_context_is_ignored_when_assisted_is_disabled؛ المدخلات المهمة: policy.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = policy.decide(
        fingerprint_match=False,
        historical_context_available=True,
        assisted_enabled=False,
    )

    assert result.decision == AnalysisDecision.FULL


def test_no_context_requires_full_analysis(policy):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_no_context_requires_full_analysis؛ المدخلات المهمة: policy.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = policy.decide(
        fingerprint_match=False,
        historical_context_available=False,
        assisted_enabled=True,
    )

    assert result.decision == AnalysisDecision.FULL
