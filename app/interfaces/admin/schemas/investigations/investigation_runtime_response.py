"""
مخططات عرض التحقيقات.

تجمع نماذج المرشح والملخص والحالة التشغيلية والتفاصيل الكاملة للتحقيق كي
تستطيع API عرض دورة التحقيق دون كشف نماذج قاعدة البيانات مباشرة.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InvestigationRuntimeResponse(BaseModel):
    """
    يمثل بيانات التشغيل المرحلية للتحقيق.
    """
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

