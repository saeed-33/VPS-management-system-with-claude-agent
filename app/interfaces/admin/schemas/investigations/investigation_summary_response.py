"""
مخططات عرض التحقيقات.

تجمع نماذج المرشح والملخص والحالة التشغيلية والتفاصيل الكاملة للتحقيق كي
تستطيع API عرض دورة التحقيق دون كشف نماذج قاعدة البيانات مباشرة.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InvestigationSummaryResponse(BaseModel):
    """
    يمثل ملخص التحقيق وحالته ونتيجته الأساسية.
    """
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

