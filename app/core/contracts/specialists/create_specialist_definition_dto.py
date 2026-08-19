"""Contract class extracted from specialists.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

import re

from .helpers import validate_specialist_slug

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
