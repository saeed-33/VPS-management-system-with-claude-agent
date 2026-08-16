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


class SpecialistCreateRequest(BaseModel):
    """
    يمثل SpecialistCreateRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة Administration interface.

        تُستدعى عندما يصل workflow إلى normalize_slug؛ المدخلات المهمة: value.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return value.strip().lower()

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        """
        يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة Administration interface.

        تُستدعى عندما يصل workflow إلى normalize_name؛ المدخلات المهمة: value.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return value.strip()


class SpecialistUpdateRequest(BaseModel):
    """
    يمثل SpecialistUpdateRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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


class SpecialistEnabledRequest(BaseModel):
    """
    يمثل SpecialistEnabledRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    enabled: bool


class SpecialistResponse(BaseModel):
    """
    يمثل SpecialistResponse مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
