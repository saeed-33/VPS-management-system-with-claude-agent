"""Contract class extracted from specialists.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

import re

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
