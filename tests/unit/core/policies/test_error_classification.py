"""Tests for test error classification.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.contracts.analysis، app.core.contracts.remediation، app.core.policies.error_classification، app.infrastructure.database.models.report_analysis، app.infrastructure.database.repositories.analysis_repository، app.interfaces.admin.schemas.reports.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace

from app.core.contracts.analysis.analysis_health_status import AnalysisHealthStatus
from app.core.contracts.analysis.analysis_issue import AnalysisIssue
from app.core.contracts.analysis.analysis_severity import AnalysisSeverity
from app.core.contracts.analysis.error_classification import ErrorClassification
from app.core.contracts.analysis.report_analysis_result import ReportAnalysisResult
from app.core.contracts.remediation.remediation_risk import RemediationRisk
from app.core.policies.error_classification import classify_issue, classify_result
from app.infrastructure.database.models.report_analysis.analysis import ReportAnalysisModel
from app.infrastructure.database.repositories.analysis_repository.repository import AnalysisRepository
from app.interfaces.admin.schemas.reports.report_analysis_response import ReportAnalysisResponse


def issue(severity=AnalysisSeverity.INFO, **values):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى issue؛ المدخلات المهمة: severity.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return AnalysisIssue(
        severity=severity,
        title=values.get("title", "Routine check"),
        description=values.get("description", "The service is healthy."),
        evidence=values.get("evidence"),
        recommendation=values.get("recommendation"),
    )


def test_classification_is_separate_from_severity_and_risk():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_classification_is_separate_from_severity_and_risk؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    classified = classify_issue(
        issue(
            title="Credential file is exposed",
            description="A token was found in the environment.",
        )
    )

    assert classified is ErrorClassification.SENSITIVE
    assert AnalysisSeverity.INFO.value == "info"
    assert RemediationRisk.LOW.value == "low"


def test_classification_is_deterministic_and_sensitive_takes_precedence():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_classification_is_deterministic_and_sensitive_takes_precedence؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert classify_issue(issue(severity=AnalysisSeverity.CRITICAL, title="Service failed")) is ErrorClassification.DANGEROUS
    assert classify_issue(issue(description="production down and password exposed")) is ErrorClassification.SENSITIVE
    assert classify_issue(issue()) is ErrorClassification.NORMAL


def test_classification_is_persisted_and_reloaded_in_issue_json():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_classification_is_persisted_and_reloaded_in_issue_json؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    model = ReportAnalysisModel(
        report_id=1,
        server_id=1,
        provider_name="test",
        model_name="test",
        status="pending",
    )

    class Session:
        """
        يمثل Session جزءًا من طبقة Test suite.

        يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
        تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
        """
        def __enter__(self):
            """
            ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

            تُستدعى عندما يصل المسار إلى __enter__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
            تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
            """
            return self

        def __exit__(self, *args):
            """
            ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

            تُستدعى عندما يصل المسار إلى __exit__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
            تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
            """
            return False

        def get(self, model_type, model_id):
            """
            ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

            تُستدعى عندما يصل المسار إلى get؛ المدخلات المهمة: model_type، model_id.
            تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
            """
            return model

        def commit(self):
            """
            ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

            تُستدعى عندما يصل المسار إلى commit؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
            تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
            """
            return None

    @contextmanager
    def session_factory():
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى session_factory؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        yield Session()

    result = ReportAnalysisResult(
        health_status=AnalysisHealthStatus.WARNING,
        summary="A sensitive issue was observed.",
        issues=[issue(description="The API token is invalid.")],
    )
    AnalysisRepository(session_factory=session_factory).mark_completed(
        analysis_id=1,
        result=result,
        finished_at=datetime.now(timezone.utc),
        duration_ms=1.0,
    )

    assert model.issues[0]["classification"] == "sensitive"
    reloaded = AnalysisIssue.model_validate(model.issues[0])
    assert reloaded.classification is ErrorClassification.SENSITIVE


def test_classify_result_adds_a_class_to_every_issue():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_classify_result_adds_a_class_to_every_issue؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = classify_result(
        ReportAnalysisResult(
            health_status=AnalysisHealthStatus.HEALTHY,
            summary="ok",
            issues=[issue(), issue(title="Disk full", severity=AnalysisSeverity.WARNING)],
        )
    )
    assert [item.classification for item in result.issues] == [
        ErrorClassification.NORMAL,
        ErrorClassification.DANGEROUS,
    ]


def test_report_analysis_read_model_exposes_classification():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_report_analysis_read_model_exposes_classification؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    model = SimpleNamespace(
        id=1,
        report_id=2,
        server_id=3,
        provider_name="test",
        model_name="test",
        status="completed",
        health_status="warning",
        summary="Sensitive issue",
        issues=[{"title": "Token exposed", "classification": "sensitive"}],
        positive_findings=[],
        recommended_actions=[],
        analysis_error=None,
        duration_ms=1.0,
        attempts=1,
        report_fingerprint=None,
        analysis_source="generated",
        reused_from_analysis_id=None,
        retrieval_strategy=None,
        retrieval_score=None,
        llm_called=True,
    )

    response = ReportAnalysisResponse.model_validate(model)
    assert response.issues[0]["classification"] == "sensitive"
