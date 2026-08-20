"""
توجيه تقرير المراقبة إلى الاختصاصيين المناسبين.

يستخرج إشارات الصحة والأخطاء والقضايا القابلة للفعل، يطابقها مع مجالات
الاختصاصيين، ثم يعيد قرار توجيه مفسرًا وقابلًا للتتبع.
"""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import re

from typing import Any, Iterable

from app.capabilities.investigation.specialist_registry.specialist_registry import SpecialistRegistry
from app.capabilities.investigation.specialist_registry.specialist_registry_snapshot import SpecialistRegistrySnapshot
from app.capabilities.investigation.specialist_registry.specialist_runtime_definition import SpecialistRuntimeDefinition

from ._issue_signal import _IssueSignal

from .constants import _BOUNDARY_RE

from .constants import _SPACE_RE

def _normalize_text(value: str | None) -> str:
    """
    يطبع نص الإشارة قبل المقارنة.
    """
    if not value:
        return ""
    text = _BOUNDARY_RE.sub(" ", value.casefold())
    return _SPACE_RE.sub(" ", text).strip()

def _contains_phrase(normalized_text: str, phrase: str) -> bool:
    """
    يتحقق من وجود عبارة مطبعة داخل النص.
    """
    needle = _normalize_text(phrase)
    return bool(needle) and f" {needle} " in f" {normalized_text} "

def _value(obj: Any, key: str, default: Any = None) -> Any:
    """
    يستخرج قيمة التعداد أو القيمة الأصلية.
    """
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def _issue_signals(analysis: Any) -> tuple[_IssueSignal, ...]:
    """
    يستخرج إشارات قابلة للفعل من القضايا ونتائج التقرير.
    """
    result = []
    for index, issue in enumerate(_value(analysis, "issues", []) or []):
        severity = str(_value(issue, "severity", "")).casefold()
        parts = [
            _value(issue, "title", ""),
            _value(issue, "description", ""),
            _value(issue, "evidence", ""),
        ]
        text = _normalize_text(" ".join(str(p) for p in parts if p))
        result.append(_IssueSignal(index=index, severity=severity, text=text))
    return tuple(result)

def _report_signal_text(report: Any) -> str:
    """
    يجمع النصوص التشغيلية من التقرير لاستخدامها في المطابقة.
    """
    parts: list[str] = []
    status = _value(report, "status", None)
    if status:
        parts.append(str(status).replace("_", " "))
    error_message = _value(report, "error_message", None)
    if error_message:
        parts.append(str(error_message))

    for execution in (_value(report, "executions", []) or []):
        if bool(_value(execution, "success", True)):
            continue
        for key in ("command_name", "stderr", "error_message"):
            value = _value(execution, key, None)
            if value:
                parts.append(str(value))
    return _normalize_text(" ".join(parts))

def _report_failed(report: Any) -> bool:
    """
    يحدد ما إذا كان التقرير أو اتصال السيرفر فاشلًا.
    """
    if not bool(_value(report, "connection_successful", True)):
        return True
    status = str(_value(report, "status", "")).casefold()
    if status in {"failed", "connection_failed", "partial_failure"}:
        return True
    return int(_value(report, "commands_failed", 0) or 0) > 0

def _health_status(analysis: Any) -> str:
    """
    يستخرج حالة الصحة من التقرير أو يعيد قيمة غير معروفة.
    """
    return str(_value(analysis, "health_status", "") or "").casefold()

def _actionable_issues(issues: Iterable[_IssueSignal]) -> tuple[_IssueSignal, ...]:
    """
    ينتقي القضايا التي تتطلب تحقيقًا أو إجراءً.
    """
    return tuple(x for x in issues if x.severity in {"warning", "critical"})
