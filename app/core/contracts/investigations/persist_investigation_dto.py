"""Contract class extracted from investigations.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from .persist_investigation_candidate_dto import PersistInvestigationCandidateDTO

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
