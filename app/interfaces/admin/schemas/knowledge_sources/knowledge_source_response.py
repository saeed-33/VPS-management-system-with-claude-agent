"""
مخططات إدارة مصادر المعرفة.

تتحقق من طلبات إنشاء وتعديل وتفعيل المصدر، وتحدد شكل بيانات المصدر التي تعود
إلى الواجهة الإدارية.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class KnowledgeSourceResponse(BaseModel):
    """
    يمثل مصدر المعرفة في استجابة API.
    """
    id: int
    slug: str
    name: str
    description: str | None
    source_type: str
    source_uri: str | None
    inline_content: str | None
    enabled: bool
    domains: list[str]
    specialist_slugs: list[str]
    tags: list[str]
    priority: int
    metadata: dict = Field(
        validation_alias="source_metadata"
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

