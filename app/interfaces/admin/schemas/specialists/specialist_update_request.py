"""
مخططات تعريفات الاختصاصيين.

تحدد طلبات إنشاء وتعديل وتفعيل الاختصاصي، وتطبع المعرف والاسم قبل تمريرهما إلى
خدمة تعريفات المجال.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class SpecialistUpdateRequest(BaseModel):
    """
    يمثل طلب تعديل تعريف اختصاصي.
    """
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    description: str | None = None
    instructions: str | None = None
    enabled: bool | None = None
    domains: list[str] | None = None
    trigger_hints: list[str] | None = None
    knowledge_topics: list[str] | None = None
    allowed_tool_ids: list[str] | None = None
    priority: int | None = None
    max_rounds: int | None = Field(
        default=None,
        ge=1,
    )
    max_actions: int | None = Field(
        default=None,
        ge=0,
    )
    metadata: dict | None = None

