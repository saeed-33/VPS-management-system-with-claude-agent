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


class KnowledgeSourceUpdateRequest(BaseModel):
    """
    يمثل الحقول القابلة للتعديل في مصدر معرفة.
    """
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    source_type: str | None = None
    source_uri: str | None = None
    inline_content: str | None = None
    enabled: bool | None = None
    domains: list[str] | None = None
    specialist_slugs: list[str] | None = None
    tags: list[str] | None = None
    priority: int | None = Field(
        default=None,
        ge=0,
    )
    metadata: dict | None = None

