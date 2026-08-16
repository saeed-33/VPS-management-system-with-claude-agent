"""
جزء من واجهة الإدارة يعرّف route أو payload أو عرضًا للمشغل.

الموقع في المعمارية: Administration interface.
يُستدعى بواسطة: FastAPI أو متصفح الإدارة.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: العرض والتحقق الشكلي لا يمنحان صلاحية تنفيذ؛ authorization في الخدمة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
    يمثل KnowledgeSourceCreateRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة Administration interface.

        تُستدعى عندما يصل workflow إلى normalize_lower؛ المدخلات المهمة: value.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return value.strip().lower()


class KnowledgeSourceUpdateRequest(BaseModel):
    """
    يمثل KnowledgeSourceUpdateRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
    يمثل KnowledgeSourceEnabledRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    enabled: bool


class KnowledgeSourceResponse(BaseModel):
    """
    يمثل KnowledgeSourceResponse مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
