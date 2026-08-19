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

