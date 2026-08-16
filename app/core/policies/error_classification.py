"""
Policy أو registry حتمي يقرر السماح أو الرفض أو التصنيف قبل التنفيذ.

الموقع في المعمارية: Core policy.
يُستدعى بواسطة: capabilities وMCP handlers.
يعتمد مباشرة على: app.core.contracts.analysis.
الحد المعماري: لا تنفذ SSH أو LLM أو persistence.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from app.core.contracts.analysis import (
    AnalysisIssue,
    ErrorClassification,
    ReportAnalysisResult,
)


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
    """Derive the specification class without changing severity or risk."""
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
    """Return a result with every issue carrying a deterministic class."""
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
