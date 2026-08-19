"""
مخططات عرض التحقيقات.

تجمع نماذج المرشح والملخص والحالة التشغيلية والتفاصيل الكاملة للتحقيق كي
تستطيع API عرض دورة التحقيق دون كشف نماذج قاعدة البيانات مباشرة.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InvestigationDetailResponse(BaseModel):
    """
    يمثل تفاصيل التحقيق الموسعة مع الأدلة والاختصاصات والنتيجة.
    """
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

