"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.contracts.autonomous_remediation، app.core.policies.autonomous_remediation.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from datetime import datetime, timezone

import pytest

from tests.test_autonomous_remediation_policy import context
from app.core.contracts.autonomous_remediation import AutonomousDecisionOutcome
from app.core.policies.autonomous_remediation import AutonomousRemediationPolicyEvaluator


@pytest.mark.parametrize(
    ("classification", "reason"),
    [
        ("dangerous", "dangerous_error_classification"),
        ("sensitive", "sensitive_error_classification"),
    ],
)
def test_dangerous_or_sensitive_classification_cannot_auto_execute(
    classification,
    reason,
):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_dangerous_or_sensitive_classification_cannot_auto_execute؛ المدخلات المهمة: classification، reason.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    decision = AutonomousRemediationPolicyEvaluator().evaluate(
        context(error_classification=classification)
    )
    assert decision.outcome is AutonomousDecisionOutcome.DENY
    assert decision.reason_codes == (reason,)
    assert decision.metadata["error_classification"] == classification
