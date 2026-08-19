"""Contract class extracted from investigation_read_models.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

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
