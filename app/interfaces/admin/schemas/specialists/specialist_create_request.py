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


class SpecialistCreateRequest(BaseModel):
    """
    يمثل طلب إنشاء تعريف اختصاصي.
    """
    slug: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,99}$",
    )
    name: str = Field(
        min_length=1,
        max_length=150,
    )
    description: str | None = None
    instructions: str | None = None
    enabled: bool = True
    domains: list[str] = Field(
        default_factory=list
    )
    trigger_hints: list[str] = Field(
        default_factory=list
    )
    knowledge_topics: list[str] = Field(
        default_factory=list
    )
    allowed_tool_ids: list[str] = Field(
        default_factory=list
    )
    priority: int = 100
    max_rounds: int = Field(
        default=2,
        ge=1,
    )
    max_actions: int = Field(
        default=4,
        ge=0,
    )
    metadata: dict = Field(
        default_factory=dict
    )

    @field_validator("slug")
    @classmethod
    def normalize_slug(
        cls,
        value: str,
    ) -> str:
        """
        يطبع slug الاختصاصي ويضمن شكله المخصص للمعرف.
        """
        return value.strip().lower()

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        """
        ينظف اسم الاختصاصي قبل التحقق والحفظ.
        """
        return value.strip()

