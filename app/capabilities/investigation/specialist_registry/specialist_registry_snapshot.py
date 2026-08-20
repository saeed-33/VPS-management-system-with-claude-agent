"""Class extracted from specialist_registry during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from types import MappingProxyType

from typing import Any, Iterable, Mapping

from app.core.contracts.specialists.helpers import validate_specialist_slug

from .specialist_domain_match import SpecialistDomainMatch

from .specialist_registry_validation_error import SpecialistRegistryValidationError

from .specialist_runtime_definition import SpecialistRuntimeDefinition

from .registry_field_parsers import _token

@dataclass(slots=True, frozen=True)
class SpecialistRegistrySnapshot:
    """
    يمثل لقطة ثابتة للاختصاصيين المفعّلين وفهارس مجالاتهم.
    """
    definitions: tuple[SpecialistRuntimeDefinition, ...]
    _by_slug: Mapping[str, SpecialistRuntimeDefinition]

    @classmethod
    def build(cls, definitions: Iterable[SpecialistRuntimeDefinition]) -> "SpecialistRegistrySnapshot":
        """
        يبني لقطة الاختصاصيين وفهارس المجالات من التعريفات المفعلة.
        """
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
        """
        يجلب اختصاصيًا من اللقطة أو السجل بمعرفه.
        """
        return self._by_slug.get(slug.strip().lower())

    def find_by_domain(self, domain: str) -> tuple[SpecialistRuntimeDefinition, ...]:
        """
        يطابق الاختصاصيين مع مجال واحد.
        """
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
        """
        يرتب الاختصاصيين حسب تغطية مجموعة مجالات.
        """
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
