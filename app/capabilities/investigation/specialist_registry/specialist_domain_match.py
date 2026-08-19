"""Class extracted from specialist_registry during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from types import MappingProxyType

from typing import Any, Iterable, Mapping

from app.infrastructure.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)

from app.core.contracts.specialists.helpers import validate_specialist_slug

from .specialist_runtime_definition import SpecialistRuntimeDefinition

@dataclass(slots=True, frozen=True)
class SpecialistDomainMatch:
    """
    يمثل مقدار تطابق اختصاصي مع المجالات المطلوبة.
    """
    specialist: SpecialistRuntimeDefinition
    matched_domains: tuple[str, ...]
    requested_domains: tuple[str, ...]

    @property
    def matched_count(self) -> int:
        """
        ينفذ عملية matched count ضمن دورة التحقيق وجمع الأدلة.
        """
        return len(self.matched_domains)

    @property
    def coverage(self) -> float:
        """
        ينفذ عملية coverage ضمن دورة التحقيق وجمع الأدلة.
        """
        if not self.requested_domains:
            return 0.0
        return self.matched_count / len(self.requested_domains)
