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


_ALLOWED_SOURCE_TYPES = {
    "url",
    "file",
    "inline",
}


def _normalize_list(
    values: list[str] | tuple[str, ...],
    *,
    lowercase: bool = True,
) -> tuple[str, ...]:
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core application contracts.

    تُستدعى عندما يصل workflow إلى _normalize_list؛ المدخلات المهمة: values، lowercase.
    تعيد tuple[str, ...] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    result: list[str] = []
    seen: set[str] = set()

    for raw in values:
        if not isinstance(raw, str):
            raise ValueError(
                "Knowledge source list values must be strings."
            )

        value = raw.strip()

        if not value:
            continue

        if lowercase:
            value = value.casefold()

        key = value.casefold()

        if key in seen:
            continue

        seen.add(key)
        result.append(value)

    return tuple(result)


@dataclass(slots=True, frozen=True)
class CreateKnowledgeSourceDTO:
    """
    يمثل CreateKnowledgeSourceDTO مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    slug: str
    name: str
    source_type: str
    description: str | None = None
    source_uri: str | None = None
    inline_content: str | None = None
    enabled: bool = True
    domains: tuple[str, ...] = ()
    specialist_slugs: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    priority: int = 100
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
        source_type = self.source_type.strip().lower()

        if not slug:
            raise ValueError(
                "Knowledge source slug must not be empty."
            )

        if not name:
            raise ValueError(
                "Knowledge source name must not be empty."
            )

        if source_type not in _ALLOWED_SOURCE_TYPES:
            raise ValueError(
                "source_type must be one of: "
                "url, file, inline."
            )

        if self.priority < 0:
            raise ValueError(
                "priority must be >= 0."
            )

        source_uri = (
            self.source_uri.strip()
            if isinstance(self.source_uri, str)
            and self.source_uri.strip()
            else None
        )

        inline_content = (
            self.inline_content.strip()
            if isinstance(self.inline_content, str)
            and self.inline_content.strip()
            else None
        )

        if (
            source_type in {"url", "file"}
            and source_uri is None
        ):
            raise ValueError(
                "url/file knowledge source requires source_uri."
            )

        if (
            source_type == "inline"
            and inline_content is None
        ):
            raise ValueError(
                "inline knowledge source requires inline_content."
            )

        object.__setattr__(self, "slug", slug)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "source_type", source_type)
        object.__setattr__(self, "source_uri", source_uri)
        object.__setattr__(
            self,
            "inline_content",
            inline_content,
        )
        object.__setattr__(
            self,
            "domains",
            _normalize_list(self.domains),
        )
        object.__setattr__(
            self,
            "specialist_slugs",
            _normalize_list(
                self.specialist_slugs
            ),
        )
        object.__setattr__(
            self,
            "tags",
            _normalize_list(self.tags),
        )


@dataclass(slots=True, frozen=True)
class UpdateKnowledgeSourceDTO:
    """
    يمثل UpdateKnowledgeSourceDTO مسؤولية محددة داخل طبقة Core application contracts.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه capabilities وinterfaces وadapters
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    name: str | None = None
    description: str | None = None
    source_type: str | None = None
    source_uri: str | None = None
    inline_content: str | None = None
    enabled: bool | None = None
    domains: tuple[str, ...] | None = None
    specialist_slugs: tuple[str, ...] | None = None
    tags: tuple[str, ...] | None = None
    priority: int | None = None
    metadata: dict | None = None

    def __post_init__(self) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core application contracts.

        تُستدعى عندما يصل workflow إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if (
            self.priority is not None
            and self.priority < 0
        ):
            raise ValueError(
                "priority must be >= 0."
            )

        if self.source_type is not None:
            source_type = (
                self.source_type
                .strip()
                .lower()
            )

            if source_type not in _ALLOWED_SOURCE_TYPES:
                raise ValueError(
                    "source_type must be one of: "
                    "url, file, inline."
                )

            object.__setattr__(
                self,
                "source_type",
                source_type,
            )

        if self.name is not None:
            name = self.name.strip()

            if not name:
                raise ValueError(
                    "Knowledge source name must not be empty."
                )

            object.__setattr__(
                self,
                "name",
                name,
            )

        for field_name in (
            "domains",
            "specialist_slugs",
            "tags",
        ):
            values = getattr(
                self,
                field_name,
            )

            if values is not None:
                object.__setattr__(
                    self,
                    field_name,
                    _normalize_list(values),
                )
