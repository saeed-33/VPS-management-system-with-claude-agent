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


class SpecialistResponse(BaseModel):
    """
    يمثل تعريف الاختصاصي في استجابة API.
    """
    id: int
    slug: str
    name: str
    description: str | None
    instructions: str | None
    enabled: bool
    domains: list[str]
    trigger_hints: list[str]
    knowledge_topics: list[str]
    allowed_tool_ids: list[str]
    priority: int
    max_rounds: int
    max_actions: int
    metadata: dict = Field(
        validation_alias="specialist_metadata"
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

