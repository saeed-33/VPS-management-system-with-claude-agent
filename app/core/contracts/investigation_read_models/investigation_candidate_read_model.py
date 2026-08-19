"""Contract class extracted from investigation_read_models.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

@dataclass(slots=True, frozen=True)
class InvestigationCandidateReadModel:
    """
    عرض مرشح متخصص مع درجته وأسباب مطابقته وحالة اختياره.
    """
    specialist_definition_id: int | None
    specialist_slug: str
    specialist_name: str
    score: int
    priority: int
    candidate_rank: int
    is_selected: bool
    selected_rank: int | None
    matched_domains: tuple[str, ...] = ()
    matched_trigger_hints: tuple[str, ...] = ()
    matched_issue_indexes: tuple[int, ...] = ()
