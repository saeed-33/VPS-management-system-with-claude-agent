"""عقود حفظ قرار بدء التحقيق والمرشحين الذين أنتجهم التوجيه."""
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


@dataclass(slots=True, frozen=True)
class PersistInvestigationDTO:
    """
    سجل قرار إنشاء التحقيق وحدوده ونتائج توجيهه.

    يربط العقد التحقيق بالتقرير والتحليل، ويحفظ المجالات والأسباب والمرشحين
    والميزانية حتى يمكن استعادة سبب بدء التحقيق واختياراته.
    """
    investigation_id: str
    server_id: int
    report_id: int
    analysis_id: int | None
    status: str
    should_investigate: bool
    routing_reasons: tuple[str, ...]
    detected_domains: tuple[str, ...]
    unmatched_issue_indexes: tuple[int, ...]
    registry_size: int
    candidate_limit: int
    selection_limit: int
    max_specialists: int
    max_rounds: int
    max_actions: int
    routing_version: str
    candidates: tuple[PersistInvestigationCandidateDTO, ...] = ()
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """يتحقق من روابط التحقيق وحدود المرشحين وترتيب ميزانيته."""
        if not self.investigation_id.strip():
            raise ValueError("investigation_id must not be empty.")
        if self.server_id < 1:
            raise ValueError("server_id must be >= 1.")
        if self.report_id < 1:
            raise ValueError("report_id must be >= 1.")
        if self.analysis_id is not None and self.analysis_id < 1:
            raise ValueError("analysis_id must be >= 1 when provided.")
        if self.candidate_limit < 1:
            raise ValueError("candidate_limit must be >= 1.")
        if self.selection_limit < 1:
            raise ValueError("selection_limit must be >= 1.")
        if self.candidate_limit < self.selection_limit:
            raise ValueError("candidate_limit must be >= selection_limit.")
