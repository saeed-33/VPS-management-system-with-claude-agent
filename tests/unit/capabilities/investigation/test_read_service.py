"""Tests for test read service.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.investigation.read_service.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from datetime import datetime, timezone

from app.capabilities.investigation.read_service import (
    InvestigationReadService,
)


class Candidate:
    """
    يمثل Candidate جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    specialist_definition_id = 10
    specialist_slug = "nginx"
    specialist_name = "NGINX Specialist"
    score = 5
    priority = 100
    candidate_rank = 1
    is_selected = True
    selected_rank = 1
    matched_domains = ["nginx", "http"]
    matched_trigger_hints = []
    matched_issue_indexes = [0]


class Model:
    """
    يمثل Model جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    investigation_id = "inv-1"
    server_id = 2
    report_id = 1076
    analysis_id = 907
    status = "completed"
    should_investigate = True
    routing_reasons = ["actionable_issue"]
    detected_domains = ["nginx"]
    unmatched_issue_indexes = []
    registry_size = 8
    candidate_limit = 12
    selection_limit = 4
    max_specialists = 4
    max_rounds = 3
    max_actions = 12
    routing_version = "deterministic-v1"
    candidates = [Candidate()]
    created_at = datetime(
        2026,
        8,
        10,
        tzinfo=timezone.utc,
    )
    updated_at = created_at
    investigation_metadata = {}


class Repository:
    """
    يمثل Repository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, model):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: model.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.model = model

    def get_by_investigation_id(
        self,
        investigation_id,
    ):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_by_investigation_id؛ المدخلات المهمة: investigation_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        if (
            investigation_id
            == self.model.investigation_id
        ):
            return self.model
        return None

    def list_recent(
        self,
        *,
        limit,
        server_id=None,
    ):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_recent؛ المدخلات المهمة: limit، server_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return [self.model]

    def list_by_report_id(
        self,
        report_id,
    ):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_by_report_id؛ المدخلات المهمة: report_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        if report_id == self.model.report_id:
            return [self.model]
        return []


def test_read_model_does_not_invent_runtime():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_read_model_does_not_invent_runtime؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    model = Model()
    model.investigation_metadata = {}

    output = InvestigationReadService(
        Repository(model)
    ).get("inv-1")

    assert output is not None
    assert output.runtime_available is False
    assert (
        output.final_diagnosis_available
        is False
    )
    assert output.runtime is None


def test_runtime_snapshot_is_exposed_when_persisted():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_snapshot_is_exposed_when_persisted؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    model = Model()
    model.investigation_metadata = {
        "runtime_snapshot": {
            "status": "completed",
            "orchestrator": "claude",
            "execution_mode": (
                "dynamic-secondary"
            ),
            "waves_completed": 2,
            "actions_used": 4,
            "evidence_count": 7,
            "specialist_runs": [
                {
                    "specialist_slug": (
                        "nginx"
                    ),
                    "status": "completed",
                }
            ],
            "evidence": [
                {
                    "evidence_id": "e1"
                }
            ],
            "correlated_claims": [
                {
                    "claim_id": "c1",
                    "certainty": (
                        "confirmed"
                    ),
                }
            ],
            "conflicts": [],
            "final_diagnosis": {
                "summary": "Stable."
            },
            "narrative": {
                "summary": "Stable."
            },
        }
    }

    output = InvestigationReadService(
        Repository(model)
    ).get("inv-1")

    assert output is not None
    assert output.runtime_available is True
    assert (
        output.final_diagnosis_available
        is True
    )
    assert output.runtime is not None
    assert (
        output.runtime.orchestrator
        == "claude"
    )
    assert (
        output.runtime.execution_mode
        == "dynamic-secondary"
    )


def test_failed_runtime_snapshot_is_not_reported_as_available():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_failed_runtime_snapshot_is_not_reported_as_available؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    model = Model()
    model.investigation_metadata = {
        "runtime_snapshot": {
            "status": "investigating",
            "runtime_available": False,
            "final_diagnosis_available": False,
            "specialist_runs": [
                {
                    "specialist_slug": "nginx",
                    "status": "failed",
                }
            ],
        }
    }

    output = InvestigationReadService(
        Repository(model)
    ).get("inv-1")

    assert output is not None
    assert output.runtime_available is False
    assert output.final_diagnosis_available is False
    assert output.runtime is not None
    assert output.runtime.specialist_runs[0]["status"] == "failed"


def test_summary_exposes_selected_specialists():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_summary_exposes_selected_specialists؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    model = Model()
    model.investigation_metadata = {}

    output = InvestigationReadService(
        Repository(model)
    ).list_recent(
        limit=25,
        server_id=2,
    )

    assert len(output) == 1
    assert (
        output[0].selected_specialists
        == ("nginx",)
    )


def test_list_limit_is_bounded():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_list_limit_is_bounded؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    service = InvestigationReadService(
        Repository(Model())
    )

    for value in (0, 501):
        try:
            service.list_recent(
                limit=value
            )
        except ValueError as exc:
            assert "between 1 and 500" in (
                str(exc)
            )
        else:
            raise AssertionError(
                "Invalid list limit accepted."
            )
