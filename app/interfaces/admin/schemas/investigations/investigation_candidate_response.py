"""
مخططات عرض التحقيقات.

تجمع نماذج المرشح والملخص والحالة التشغيلية والتفاصيل الكاملة للتحقيق كي
تستطيع API عرض دورة التحقيق دون كشف نماذج قاعدة البيانات مباشرة.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InvestigationCandidateResponse(BaseModel):
    """
    يمثل مرشح تحقيق مقترحًا للعرض الإداري.
    """
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

