"""Contract class extracted from investigation_read_models.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from .investigation_candidate_read_model import InvestigationCandidateReadModel

from .investigation_runtime_read_model import InvestigationRuntimeReadModel

@dataclass(slots=True, frozen=True)
class InvestigationDetailReadModel:
    """
    العرض الكامل للتحقيق مع قرار التوجيه والمرشحين وحالة التنفيذ والتشخيص.

    يجمع هذا العقد المعلومات التي يحتاجها المستخدم لمراجعة لماذا بدأ التحقيق،
    من شارك فيه، وما الأدلة والنتيجة التي وصل إليها.
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
    candidates: tuple[InvestigationCandidateReadModel, ...]
    runtime_available: bool
    final_diagnosis_available: bool
    runtime: InvestigationRuntimeReadModel | None
    metadata: dict
    created_at: datetime
    updated_at: datetime
