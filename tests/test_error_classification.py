from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace

from app.core.contracts.analysis import (
    AnalysisHealthStatus,
    AnalysisIssue,
    AnalysisSeverity,
    ErrorClassification,
    ReportAnalysisResult,
)
from app.core.contracts.remediation import RemediationRisk
from app.core.policies.error_classification import classify_issue, classify_result
from app.infrastructure.database.models.report_analysis import ReportAnalysisModel
from app.infrastructure.database.repositories.analysis_repository import AnalysisRepository
from app.interfaces.admin.schemas.reports import ReportAnalysisResponse


def issue(severity=AnalysisSeverity.INFO, **values):
    return AnalysisIssue(
        severity=severity,
        title=values.get("title", "Routine check"),
        description=values.get("description", "The service is healthy."),
        evidence=values.get("evidence"),
        recommendation=values.get("recommendation"),
    )


def test_classification_is_separate_from_severity_and_risk():
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
    assert classify_issue(issue(severity=AnalysisSeverity.CRITICAL, title="Service failed")) is ErrorClassification.DANGEROUS
    assert classify_issue(issue(description="production down and password exposed")) is ErrorClassification.SENSITIVE
    assert classify_issue(issue()) is ErrorClassification.NORMAL


def test_classification_is_persisted_and_reloaded_in_issue_json():
    model = ReportAnalysisModel(
        report_id=1,
        server_id=1,
        provider_name="test",
        model_name="test",
        status="pending",
    )

    class Session:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, model_type, model_id):
            return model

        def commit(self):
            return None

    @contextmanager
    def session_factory():
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
