"""مرشح بحث نصي موحد."""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class FullTextCandidate:
    """
    يمثل مرشحًا أعاده البحث النصي مع هويته وترتيبه وحالة تحليله التاريخي.
    """
    report_id: int
    analysis_id: int
    rank: float
    health_status: str | None
