"""Contract class extracted from investigations.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

@dataclass(slots=True, frozen=True)
class PersistInvestigationCandidateDTO:
    """
    بيانات مرشح متخصص كما ظهر في ترتيب التوجيه قبل أو بعد الاختيار.

    يحفظ العقد سبب الترتيب والمجالات المتطابقة وحالة الاختيار حتى يمكن تفسير
    لماذا شارك متخصص معين في التحقيق.
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

    def __post_init__(self) -> None:
        """يتحقق من ترتيب المرشح واتساق حالته مع رتبة الاختيار."""
        if not self.specialist_slug.strip():
            raise ValueError("specialist_slug must not be empty.")
        if not self.specialist_name.strip():
            raise ValueError("specialist_name must not be empty.")
        if self.candidate_rank < 1:
            raise ValueError("candidate_rank must be >= 1.")
        if self.is_selected and self.selected_rank is None:
            raise ValueError("selected candidate requires selected_rank.")
        if not self.is_selected and self.selected_rank is not None:
            raise ValueError("unselected candidate cannot have selected_rank.")
        if self.selected_rank is not None and self.selected_rank < 1:
            raise ValueError("selected_rank must be >= 1.")
