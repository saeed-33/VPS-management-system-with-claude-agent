"""
تصنيف أولي لمخاطر المشكلات التي أخرجها تحليل التقرير.

يميز التصنيف بين مشكلة عادية أو خطرة أو حساسة، حتى لا تمر حالات انقطاع الخدمة
أو تسرب الأسرار إلى مسار معالجة ذاتية غير مناسب.
"""
from __future__ import annotations

from app.core.contracts.analysis.analysis_issue import AnalysisIssue
from app.core.contracts.analysis.error_classification import ErrorClassification
from app.core.contracts.analysis.report_analysis_result import ReportAnalysisResult


_SENSITIVE_MARKERS = (
    "credential",
    "password",
    "passwd",
    "secret",
    "api key",
    "apikey",
    "access key",
    "private key",
    "ssh key",
    "token",
    "authorization",
    "authentication",
    "security",
    "privilege",
    "access denied",
    "unauthorized",
    "permission denied",
    "/etc/shadow",
    ".env",
    ".ssh/",
    "sensitive path",
)

_DANGEROUS_MARKERS = (
    "outage",
    "production down",
    "service down",
    "data loss",
    "data corruption",
    "disk full",
    "out of memory",
    "oom",
    "system crash",
    "service failed",
    "service failure",
    "unavailable",
    "resource exhaustion",
)


def classify_issue(issue: AnalysisIssue) -> ErrorClassification:
    """
    يفحص نص المشكلة وقرينتها لتمييز الحالة الحساسة أو الخطرة قبل اقتراح المعالجة.
    """
    text = " ".join(
        value
        for value in (
            issue.title,
            issue.description,
            issue.evidence or "",
            issue.recommendation or "",
        )
        if value
    ).casefold()

    if any(marker in text for marker in _SENSITIVE_MARKERS):
        return ErrorClassification.SENSITIVE

    if any(marker in text for marker in _DANGEROUS_MARKERS):
        return ErrorClassification.DANGEROUS

    return ErrorClassification.NORMAL


def classify_result(result: ReportAnalysisResult) -> ReportAnalysisResult:
    """
    ينسخ نتيجة التحليل مع إضافة تصنيف خطر لكل مشكلة دون تغيير بقية النتيجة.
    """
    return result.model_copy(
        update={
            "issues": [
                issue.model_copy(
                    update={"classification": classify_issue(issue)}
                )
                for issue in result.issues
            ]
        }
    )
