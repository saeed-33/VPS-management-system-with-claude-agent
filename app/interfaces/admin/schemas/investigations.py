from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InvestigationCandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class InvestigationSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class InvestigationRuntimeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str | None = None
    orchestrator: str | None = None
    execution_mode: str | None = None
    waves_completed: int | None = None
    actions_used: int | None = None
    evidence_count: int | None = None
    specialist_runs: tuple[dict[str, Any], ...] = ()
    evidence: tuple[dict[str, Any], ...] = ()
    correlated_claims: tuple[dict[str, Any], ...] = ()
    conflicts: tuple[dict[str, Any], ...] = ()
    final_diagnosis: dict[str, Any] | None = None
    narrative: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class InvestigationDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    candidates: tuple[InvestigationCandidateResponse, ...]
    runtime_available: bool
    final_diagnosis_available: bool
    runtime: InvestigationRuntimeResponse | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime
