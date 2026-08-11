from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any


@dataclass(slots=True)
class PerformanceProfile:
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
    _current_profile.set(
        PerformanceProfile(report_id=report_id)
    )


def record_timing(name: str, duration_ms: float) -> None:
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
    profile = _current_profile.get()
    if profile is None:
        return

    profile.counters[name] = value


def snapshot() -> dict[str, Any]:
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
    _current_profile.set(None)
