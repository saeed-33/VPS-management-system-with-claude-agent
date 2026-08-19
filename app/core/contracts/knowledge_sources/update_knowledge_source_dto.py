"""Contract class extracted from knowledge_sources.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from .helpers import _ALLOWED_SOURCE_TYPES

from .helpers import _normalize_list

@dataclass(slots=True, frozen=True)
class UpdateKnowledgeSourceDTO:
    """
    يمثل الحقول الاختيارية لتعديل مصدر معرفة قائم.
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
        يتحقق من الحقول المقدمة في تعديل المصدر ويطبع النوع والقيم النصية والقوائم.
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
