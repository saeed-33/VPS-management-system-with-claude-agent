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


class KnowledgeSourceCreateRequest(BaseModel):
    """
    يمثل طلب إنشاء مصدر معرفة ومحتواه ووسومه ونطاقه.
    """
    slug: str = Field(
        min_length=1,
        max_length=120,
        pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,119}$",
    )
    name: str = Field(
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    source_type: str
    source_uri: str | None = None
    inline_content: str | None = None
    enabled: bool = True
    domains: list[str] = Field(
        default_factory=list
    )
    specialist_slugs: list[str] = Field(
        default_factory=list
    )
    tags: list[str] = Field(
        default_factory=list
    )
    priority: int = Field(
        default=100,
        ge=0,
    )
    metadata: dict = Field(
        default_factory=dict
    )

    @field_validator(
        "slug",
        "source_type",
    )
    @classmethod
    def normalize_lower(
        cls,
        value: str,
    ) -> str:
        """
        يطبع قيمة النص إلى أحرف صغيرة لاستخدامها في معرفات مصدر المعرفة.
        """
        return value.strip().lower()


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


class KnowledgeSourceEnabledRequest(BaseModel):
    """
    يمثل طلب تفعيل أو تعطيل مصدر معرفة.
    """
    enabled: bool


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
