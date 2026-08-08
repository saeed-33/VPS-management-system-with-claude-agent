from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from app.shared.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)
from app.shared.dto.specialists import validate_specialist_slug


class SpecialistRegistryValidationError(ValueError):
    pass


def _token(value: str) -> str:
    return value.strip().casefold()


def _string_tuple(values: Any, field_name: str, lowercase: bool = False) -> tuple[str, ...]:
    if not isinstance(values, list):
        raise SpecialistRegistryValidationError(
            f"{field_name} must be a JSON list."
        )

    result: list[str] = []
    seen: set[str] = set()

    for raw in values:
        if not isinstance(raw, str):
            raise SpecialistRegistryValidationError(
                f"{field_name} must contain strings only."
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
class SpecialistRuntimeDefinition:
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


@dataclass(slots=True, frozen=True)
class SpecialistDomainMatch:
    specialist: SpecialistRuntimeDefinition
    matched_domains: tuple[str, ...]
    requested_domains: tuple[str, ...]

    @property
    def matched_count(self) -> int:
        return len(self.matched_domains)

    @property
    def coverage(self) -> float:
        if not self.requested_domains:
            return 0.0
        return self.matched_count / len(self.requested_domains)


@dataclass(slots=True, frozen=True)
class SpecialistRegistrySnapshot:
    definitions: tuple[SpecialistRuntimeDefinition, ...]
    _by_slug: Mapping[str, SpecialistRuntimeDefinition]

    @classmethod
    def build(cls, definitions: Iterable[SpecialistRuntimeDefinition]) -> "SpecialistRegistrySnapshot":
        ordered = tuple(sorted(
            definitions,
            key=lambda item: (
                item.priority,
                item.name.casefold(),
                item.slug,
                item.id,
            ),
        ))

        by_slug: dict[str, SpecialistRuntimeDefinition] = {}
        for definition in ordered:
            if definition.slug in by_slug:
                raise SpecialistRegistryValidationError(
                    f"Duplicate specialist slug in runtime registry: {definition.slug}"
                )
            by_slug[definition.slug] = definition

        return cls(
            definitions=ordered,
            _by_slug=MappingProxyType(by_slug),
        )

    def get_by_slug(self, slug: str) -> SpecialistRuntimeDefinition | None:
        return self._by_slug.get(slug.strip().lower())

    def find_by_domain(self, domain: str) -> tuple[SpecialistRuntimeDefinition, ...]:
        normalized = _token(domain)
        if not normalized:
            return ()

        return tuple(
            definition
            for definition in self.definitions
            if normalized in definition.domains
        )

    def find_by_domains(
        self,
        domains: Iterable[str],
        *,
        require_all: bool = False,
    ) -> tuple[SpecialistDomainMatch, ...]:
        requested_list: list[str] = []
        seen: set[str] = set()

        for raw in domains:
            if not isinstance(raw, str):
                raise ValueError("Requested domains must be strings.")

            value = _token(raw)
            if not value or value in seen:
                continue

            seen.add(value)
            requested_list.append(value)

        requested = tuple(requested_list)
        if not requested:
            return ()

        requested_set = set(requested)
        matches: list[SpecialistDomainMatch] = []

        for definition in self.definitions:
            specialist_domains = set(definition.domains)
            matched = tuple(
                domain
                for domain in requested
                if domain in specialist_domains
            )

            if not matched:
                continue

            if require_all and not requested_set.issubset(specialist_domains):
                continue

            matches.append(
                SpecialistDomainMatch(
                    specialist=definition,
                    matched_domains=matched,
                    requested_domains=requested,
                )
            )

        return tuple(sorted(
            matches,
            key=lambda match: (
                -match.matched_count,
                match.specialist.priority,
                match.specialist.name.casefold(),
                match.specialist.slug,
                match.specialist.id,
            ),
        ))


class SpecialistRegistry:
    def __init__(
        self,
        repository: SpecialistDefinitionRepository,
    ) -> None:
        self._repository = repository

    def snapshot(self) -> SpecialistRegistrySnapshot:
        definitions: list[SpecialistRuntimeDefinition] = []

        for model in self._repository.list_enabled():
            try:
                definitions.append(
                    SpecialistRuntimeDefinition.from_model(model)
                )
            except SpecialistRegistryValidationError as exc:
                identity = getattr(model, "slug", None) or getattr(model, "id", "unknown")
                raise SpecialistRegistryValidationError(
                    f"Invalid enabled specialist {identity!r}: {exc}"
                ) from exc

        return SpecialistRegistrySnapshot.build(definitions)

    def get_enabled(self) -> tuple[SpecialistRuntimeDefinition, ...]:
        return self.snapshot().definitions

    def get_by_slug(self, slug: str) -> SpecialistRuntimeDefinition | None:
        return self.snapshot().get_by_slug(slug)

    def find_by_domain(self, domain: str) -> tuple[SpecialistRuntimeDefinition, ...]:
        return self.snapshot().find_by_domain(domain)

    def find_by_domains(
        self,
        domains: Iterable[str],
        *,
        require_all: bool = False,
    ) -> tuple[SpecialistDomainMatch, ...]:
        return self.snapshot().find_by_domains(
            domains,
            require_all=require_all,
        )
