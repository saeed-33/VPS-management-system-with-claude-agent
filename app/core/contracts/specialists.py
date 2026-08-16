"""عقود تعريف المتخصصين الذين يحققون في مجالات مختلفة من عطل السيرفر."""
from __future__ import annotations

from dataclasses import dataclass, field
import re

_SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,99}$")


def validate_specialist_slug(value: str) -> None:
    """
    يتحقق من أن معرف المتخصص النصي صالح وثابت للاستخدام في التوجيه والتخزين.

    يضمن النمط الموحد أن يبقى المعرف آمنًا للروابط والسجلات ولا يتغير بسبب
    اختلاف حالة الأحرف أو إدخال رموز غير متوقعة.
    """
    if not _SLUG_PATTERN.fullmatch(value):
        raise ValueError(
            "Specialist slug must start with a lowercase letter and contain only lowercase letters, digits, '-' or '_'."
        )


@dataclass(slots=True, frozen=True)
class CreateSpecialistDefinitionDTO:
    """
    البيانات اللازمة لتسجيل متخصص ومجالاته وتلميحات تشغيله وأدواته المسموحة.

    يحدد العقد حدود الجولات والأفعال حتى لا يفتح تعريف المتخصص تحقيقًا بلا
    حدود عند استخدامه لاحقًا.
    """
    slug: str
    name: str
    description: str | None = None
    instructions: str | None = None
    enabled: bool = True
    domains: list[str] = field(default_factory=list)
    trigger_hints: list[str] = field(default_factory=list)
    knowledge_topics: list[str] = field(default_factory=list)
    allowed_tool_ids: list[str] = field(default_factory=list)
    priority: int = 100
    max_rounds: int = 2
    max_actions: int = 4
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """يطبع المعرف ويتحقق من الاسم وحدود الجولات والأفعال."""
        slug = self.slug.strip().lower()
        name = self.name.strip()
        validate_specialist_slug(slug)
        if not name:
            raise ValueError("Specialist name must not be empty.")
        if len(name) > 150:
            raise ValueError("Specialist name must be <= 150 characters.")
        if self.max_rounds < 1:
            raise ValueError("max_rounds must be >= 1.")
        if self.max_actions < 0:
            raise ValueError("max_actions must be >= 0.")


@dataclass(slots=True, frozen=True)
class UpdateSpecialistDefinitionDTO:
    """
    التغييرات الاختيارية على تعريف متخصص موجود.

    تسمح القيم المحددة بتعديل تعليماته أو مجالاته أو أدواته وحدوده، بينما تعني
    القيم الفارغة إبقاء الحقل الحالي كما هو.
    """
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    enabled: bool | None = None
    domains: list[str] | None = None
    trigger_hints: list[str] | None = None
    knowledge_topics: list[str] | None = None
    allowed_tool_ids: list[str] | None = None
    priority: int | None = None
    max_rounds: int | None = None
    max_actions: int | None = None
    metadata: dict | None = None

    def __post_init__(self) -> None:
        """يتحقق من الاسم الجديد وحدود الجولات والأفعال عند تقديمها."""
        if self.name is not None and not self.name.strip():
            raise ValueError("Specialist name must not be empty.")
        if self.name is not None and len(self.name.strip()) > 150:
            raise ValueError("Specialist name must be <= 150 characters.")
        if self.max_rounds is not None and self.max_rounds < 1:
            raise ValueError("max_rounds must be >= 1.")
        if self.max_actions is not None and self.max_actions < 0:
            raise ValueError("max_actions must be >= 0.")
