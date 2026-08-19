"""Class extracted from specialist_registry during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from types import MappingProxyType

from typing import Any, Iterable, Mapping

from app.infrastructure.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)

from app.core.contracts.specialists.helpers import validate_specialist_slug

class SpecialistRegistryValidationError(ValueError):
    """
    يمثل فشل تحقق تعريف اختصاصي أو علاقاته.
    """
    pass
