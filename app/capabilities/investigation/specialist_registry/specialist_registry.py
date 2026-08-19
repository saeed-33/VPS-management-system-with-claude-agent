"""Class extracted from specialist_registry during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from types import MappingProxyType

from typing import Any, Iterable, Mapping

from app.infrastructure.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)

from app.core.contracts.specialists.helpers import validate_specialist_slug

from .specialist_domain_match import SpecialistDomainMatch

from .specialist_registry_snapshot import SpecialistRegistrySnapshot

from .specialist_registry_validation_error import SpecialistRegistryValidationError

from .specialist_runtime_definition import SpecialistRuntimeDefinition

class SpecialistRegistry:
    """
    يبني لقطة الاختصاصيين ويوفر عمليات البحث والمطابقة.
    """
    def __init__(
        self,
        repository: SpecialistDefinitionRepository,
    ) -> None:
        """
        يهيئ SpecialistRegistry ويربط الاعتماديات اللازمة لدورة التحقيق.
        """
        self._repository = repository

    def snapshot(self) -> SpecialistRegistrySnapshot:
        """
        ينشئ لقطة تشغيلية من الاختصاصيين المفعّلين.
        """
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
        """
        يعيد الاختصاصيين المفعّلين.
        """
        return self.snapshot().definitions

    def get_by_slug(self, slug: str) -> SpecialistRuntimeDefinition | None:
        """
        يجلب اختصاصيًا من اللقطة أو السجل بمعرفه.
        """
        return self.snapshot().get_by_slug(slug)

    def find_by_domain(self, domain: str) -> tuple[SpecialistRuntimeDefinition, ...]:
        """
        يطابق الاختصاصيين مع مجال واحد.
        """
        return self.snapshot().find_by_domain(domain)

    def find_by_domains(
        self,
        domains: Iterable[str],
        *,
        require_all: bool = False,
    ) -> tuple[SpecialistDomainMatch, ...]:
        """
        يرتب الاختصاصيين حسب تغطية مجموعة مجالات.
        """
        return self.snapshot().find_by_domains(
            domains,
            require_all=require_all,
        )
