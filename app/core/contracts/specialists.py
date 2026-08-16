"""
عقود وDTOs مشتركة لنقل البيانات بين الطبقات.

الموقع في المعمارية: Core application contracts.
يُستدعى بواسطة: capabilities وinterfaces وadapters.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا تنفذ I/O أو workflow.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import re

_SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,99}$")


def validate_specialist_slug(value: str) -> None:
    """
    يقيّم أو يتحقق من شرط حتمي قبل السماح بالخطوة التالية ضمن طبقة Core application contracts.

    تُستدعى عندما يصل workflow إلى validate_specialist_slug؛ المدخلات المهمة: value.
    تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    if not _SLUG_PATTERN.fullmatch(value):
        raise ValueError(
            "Specialist slug must start with a lowercase letter and contain only lowercase letters, digits, '-' or '_'."
        )


@dataclass(slots=True, frozen=True)
class CreateSpecialistDefinitionDTO:
    """
    يمثل CreateSpecialistDefinitionDTO مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core application contracts.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
    يمثل UpdateSpecialistDefinitionDTO مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core application contracts.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if self.name is not None and not self.name.strip():
            raise ValueError("Specialist name must not be empty.")
        if self.name is not None and len(self.name.strip()) > 150:
            raise ValueError("Specialist name must be <= 150 characters.")
        if self.max_rounds is not None and self.max_rounds < 1:
            raise ValueError("max_rounds must be >= 1.")
        if self.max_actions is not None and self.max_actions < 0:
            raise ValueError("max_actions must be >= 0.")
