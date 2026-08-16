"""نماذج القراءة التي تعرض تقدم التحقيق دون كشف تفاصيل التخزين الداخلية."""
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


@dataclass(slots=True, frozen=True)
class InvestigationSummaryReadModel:
    """
    ملخص حالة التحقيق المناسب للقوائم وشاشات المتابعة السريعة.

    يبين هل يلزم التحقيق ومن اختير له وما إذا كان runtime والتشخيص النهائي
    متاحين، دون تحميل الأدلة والتفاصيل التشغيلية كلها.
    """
    investigation_id: str
    server_id: int
    report_id: int
    analysis_id: int | None
    status: str
    should_investigate: bool
    detected_domains: tuple[str, ...]
    selected_specialists: tuple[str, ...]
    max_specialists: int
    max_rounds: int
    max_actions: int
    runtime_available: bool
    final_diagnosis_available: bool
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True, frozen=True)
class InvestigationRuntimeReadModel:
    """
    تفاصيل تشغيلية قابلة للعرض عن جولات التحقيق وأدلته ونتائجه المتعارضة.
    """
    status: str | None = None
    orchestrator: str | None = None
    execution_mode: str | None = None
    waves_completed: int | None = None
    actions_used: int | None = None
    evidence_count: int | None = None
    specialist_runs: tuple[dict, ...] = ()
    evidence: tuple[dict, ...] = ()
    correlated_claims: tuple[dict, ...] = ()
    conflicts: tuple[dict, ...] = ()
    final_diagnosis: dict | None = None
    narrative: dict | None = None
    metadata: dict = field(default_factory=dict)


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
