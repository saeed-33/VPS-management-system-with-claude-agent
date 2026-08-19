"""Class extracted from specialist_registry during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from types import MappingProxyType

from typing import Any, Iterable, Mapping

from app.infrastructure.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)

from app.core.contracts.specialists.helpers import validate_specialist_slug

from .specialist_registry_validation_error import SpecialistRegistryValidationError

from .factories import _string_tuple

@dataclass(slots=True, frozen=True)
class SpecialistRuntimeDefinition:
    """
    يمثل تعريف اختصاصي مطبعًا وجاهزًا للاستخدام أثناء التحقيق.
    """
    id: int
    slug: str
    name: str
    description: str | None
    instructions: str | None
    domains: tuple[str, ...]
    trigger_hints: tuple[str, ...]
    knowledge_topics: tuple[str, ...]
    allowed_tool_ids: tuple[str, ...]
    priority: int
    max_rounds: int
    max_actions: int
    metadata: Mapping[str, Any]

    @classmethod
    def from_model(cls, model) -> "SpecialistRuntimeDefinition":
        """
        يحوّل نموذج الاختصاصي إلى تعريف تشغيل مطبع.
        """
        if not isinstance(model.id, int) or model.id < 1:
            raise SpecialistRegistryValidationError(
                "Specialist id must be a positive integer."
            )

        if not bool(model.enabled):
            raise SpecialistRegistryValidationError(
                "Disabled specialist cannot enter an enabled registry snapshot."
            )

        if not isinstance(model.slug, str):
            raise SpecialistRegistryValidationError(
                "Specialist slug must be a string."
            )

        slug = model.slug.strip().lower()

        try:
            validate_specialist_slug(slug)
        except ValueError as exc:
            raise SpecialistRegistryValidationError(str(exc)) from exc

        if not isinstance(model.name, str) or not model.name.strip():
            raise SpecialistRegistryValidationError(
                "Specialist name must not be empty."
            )

        if not isinstance(model.priority, int):
            raise SpecialistRegistryValidationError(
                "priority must be an integer."
            )

        if not isinstance(model.max_rounds, int) or model.max_rounds < 1:
            raise SpecialistRegistryValidationError(
                "max_rounds must be an integer >= 1."
            )

        if not isinstance(model.max_actions, int) or model.max_actions < 0:
            raise SpecialistRegistryValidationError(
                "max_actions must be an integer >= 0."
            )

        if not isinstance(model.specialist_metadata, dict):
            raise SpecialistRegistryValidationError(
                "metadata must be a JSON object."
            )

        return cls(
            id=model.id,
            slug=slug,
            name=model.name.strip(),
            description=model.description.strip()
            if isinstance(model.description, str) and model.description.strip()
            else None,
            instructions=model.instructions.strip()
            if isinstance(model.instructions, str) and model.instructions.strip()
            else None,
            domains=_string_tuple(model.domains, "domains", lowercase=True),
            trigger_hints=_string_tuple(model.trigger_hints, "trigger_hints"),
            knowledge_topics=_string_tuple(model.knowledge_topics, "knowledge_topics"),
            allowed_tool_ids=_string_tuple(model.allowed_tool_ids, "allowed_tool_ids"),
            priority=model.priority,
            max_rounds=model.max_rounds,
            max_actions=model.max_actions,
            metadata=MappingProxyType(dict(model.specialist_metadata)),
        )
