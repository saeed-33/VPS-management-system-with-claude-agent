"""
جزء من Retrieval/RAG لتطبيع report أو استرجاع context أو الفهرسة.

الموقع في المعمارية: Application capability / retrieval.
يُستدعى بواسطة: Analysis orchestrator وخدمات الفهرسة.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: ينتهي عند context مع provenance؛ reasoning مسؤولية أعلى.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any


@dataclass(slots=True)
class PerformanceProfile:
    """
    يمثل PerformanceProfile مسؤولية محددة داخل طبقة Application capability / retrieval.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Analysis orchestrator وخدمات الفهرسة
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

    تُستدعى عندما يصل workflow إلى start_profile؛ المدخلات المهمة: report_id.
    تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    _current_profile.set(
        PerformanceProfile(report_id=report_id)
    )


def record_timing(name: str, duration_ms: float) -> None:
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

    تُستدعى عندما يصل workflow إلى record_timing؛ المدخلات المهمة: name، duration_ms.
    تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة Application capability / retrieval.

    تُستدعى عندما يصل workflow إلى set_counter؛ المدخلات المهمة: name، value.
    تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    profile = _current_profile.get()
    if profile is None:
        return

    profile.counters[name] = value


def snapshot() -> dict[str, Any]:
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

    تُستدعى عندما يصل workflow إلى snapshot؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

    تُستدعى عندما يصل workflow إلى clear_profile؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    _current_profile.set(None)
