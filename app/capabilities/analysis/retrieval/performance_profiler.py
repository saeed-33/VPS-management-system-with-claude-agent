"""
قياس مراحل الاسترجاع والتحليل داخل سياق التنفيذ الحالي.

يحفظ أزمنة المراحل والعدادات في ملف أداء معزول لكل مهمة، ثم يقدّم لقطة قابلة
للتسجيل أو يمسحها عند انتهاء العملية.
"""
from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any


@dataclass(slots=True)
class PerformanceProfile:
    """
    يحمل أزمنة المراحل والعدادات الخاصة بعملية تحليل أو استرجاع واحدة.
    """
    report_id: int
    started_at: float = field(default_factory=perf_counter)
    timings_ms: dict[str, float] = field(default_factory=dict)
    counters: dict[str, int | float | str | bool | None] = field(
        default_factory=dict
    )


_current_profile: ContextVar[PerformanceProfile | None] = ContextVar(
    "rag_performance_profile",
    default=None,
)


def start_profile(report_id: int) -> None:
    """
    ينشئ ملف أداء جديدًا ويربطه بسياق التنفيذ الحالي مع تسجيل هوية التقرير.
    """
    _current_profile.set(
        PerformanceProfile(report_id=report_id)
    )


def record_timing(name: str, duration_ms: float) -> None:
    """
    يسجل مدة مرحلة محددة بالميلي ثانية داخل ملف الأداء الحالي.
    """
    profile = _current_profile.get()
    if profile is None:
        return

    profile.timings_ms[name] = round(
        profile.timings_ms.get(name, 0.0) + duration_ms,
        2,
    )


def set_counter(
    name: str,
    value: int | float | str | bool | None,
) -> None:
    """
    يضع عدادًا أو قيمة وصفية تساعد على تفسير تكلفة ونتيجة الاسترجاع.
    """
    profile = _current_profile.get()
    if profile is None:
        return

    profile.counters[name] = value


def snapshot() -> dict[str, Any]:
    """
    يعيد نسخة قابلة للتسلسل من أزمنة وعدادات ملف الأداء الحالي.
    """
    profile = _current_profile.get()
    if profile is None:
        return {}

    timings = dict(profile.timings_ms)
    timings["orchestrator_total_ms"] = round(
        (perf_counter() - profile.started_at) * 1000,
        2,
    )

    return {
        "report_id": profile.report_id,
        "timings_ms": timings,
        "counters": dict(profile.counters),
    }


def clear_profile() -> None:
    """
    يزيل ملف الأداء من سياق التنفيذ بعد اكتمال العملية أو فشلها.
    """
    _current_profile.set(None)
