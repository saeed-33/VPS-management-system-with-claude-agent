"""Port required to manage specialist definitions."""
from __future__ import annotations

from typing import Any, Protocol

from app.core.contracts.specialists.create_specialist_definition_dto import (
    CreateSpecialistDefinitionDTO,
)
from app.core.contracts.specialists.update_specialist_definition_dto import (
    UpdateSpecialistDefinitionDTO,
)


class SpecialistDefinitionRepositoryPort(Protocol):
    """Persistence operations required by specialist capabilities."""

    def get_by_id(self, specialist_id: int) -> Any | None: ...

    def get_by_slug(self, slug: str) -> Any | None: ...

    def list_all(self) -> list[Any]: ...

    def list_enabled(self) -> list[Any]: ...

    def create(self, data: CreateSpecialistDefinitionDTO) -> Any: ...

    def update(self, specialist_id: int, data: UpdateSpecialistDefinitionDTO) -> Any | None: ...

    def set_enabled(self, specialist_id: int, enabled: bool) -> Any | None: ...

    def delete(self, specialist_id: int) -> bool: ...

