"""Tests for test issue fingerprint service.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.remediation.issue_fingerprint_service.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from dataclasses import dataclass

from app.capabilities.remediation.issue_fingerprint_service import IssueFingerprintService


@dataclass
class Runtime:
    """
    يمثل Runtime جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    correlated_claims: tuple[dict, ...]
    final_diagnosis: dict | None


@dataclass
class Investigation:
    """
    يمثل Investigation جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    runtime: Runtime | None
    final_diagnosis_available: bool


class ReadService:
    """
    يمثل ReadService جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, investigations):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: investigations.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.investigations = investigations

    def get(self, investigation_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get؛ المدخلات المهمة: investigation_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.investigations.get(investigation_id)


def investigation(*, title="Nginx service inactive", certainty="confirmed", state="inactive", narrative="first wording", claim_id="c1", evidence_id="e1", confidence=0.9, reverse=False, extra_claim=False):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى investigation؛ المدخلات المهمة: title، certainty، state، narrative، claim_id، evidence_id.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    claims = [
        {
            "claim_id": claim_id,
            "title": title,
            "description": narrative,
            "certainty": certainty,
            "confidence": confidence,
            "evidence_ids": [evidence_id],
            "metadata": {"diagnostic_states": [state]},
        }
    ]
    if extra_claim:
        claims.append({
            "claim_id": "second-claim",
            "title": "Nginx configuration valid",
            "description": "different narrative",
            "certainty": "likely",
            "confidence": 0.4,
            "evidence_ids": ["second-evidence"],
            "metadata": {"diagnostic_states": ["configured"]},
        })
    if reverse:
        claims.reverse()
    return Investigation(Runtime(tuple(claims), {"summary": narrative}), True)


def test_equivalent_persisted_diagnoses_have_same_fingerprint():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_equivalent_persisted_diagnoses_have_same_fingerprint؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    read = ReadService({
        "a": investigation(claim_id="claim-a", evidence_id="evidence-a", narrative="one", confidence=0.8),
        "b": investigation(claim_id="claim-b", evidence_id="evidence-b", narrative="two", confidence=0.95),
        "c": investigation(claim_id="claim-c", evidence_id="evidence-c", narrative="three", confidence=0.2),
    })
    service = IssueFingerprintService(investigation_read_service=read)
    assert service.derive("a") == service.derive("b") == service.derive("c")


def test_semantic_change_changes_fingerprint():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_semantic_change_changes_fingerprint؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    read = ReadService({"a": investigation(), "b": investigation(state="failed")})
    service = IssueFingerprintService(investigation_read_service=read)
    assert service.derive("a") != service.derive("b")


def test_claim_order_does_not_change_fingerprint():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_claim_order_does_not_change_fingerprint؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    first = investigation(extra_claim=True)
    second = investigation(extra_claim=True)
    second.runtime.correlated_claims = tuple(reversed(second.runtime.correlated_claims))
    read = ReadService({"a": first, "b": second})
    service = IssueFingerprintService(investigation_read_service=read)
    assert service.derive("a") == service.derive("b")


def test_unavailable_diagnosis_returns_none():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_unavailable_diagnosis_returns_none؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    read = ReadService({"a": Investigation(None, False), "b": Investigation(Runtime((), None), True)})
    service = IssueFingerprintService(investigation_read_service=read)
    assert service.derive("a") is None
    assert service.derive("b") is None
