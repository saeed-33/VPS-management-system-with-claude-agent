from __future__ import annotations

from app.infrastructure.database.models.specialist_definition import (
    SpecialistDefinitionModel,
)
from app.infrastructure.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)
from app.core.contracts.specialists import (
    CreateSpecialistDefinitionDTO,
    UpdateSpecialistDefinitionDTO,
)
from app.core.exceptions import (
    DuplicateSpecialistDefinitionError,
    SpecialistDefinitionNotFoundError,
)


class SpecialistDefinitionService:
    def __init__(
        self,
        repository: SpecialistDefinitionRepository,
    ) -> None:
        self._repository = repository

    def list_specialists(
        self,
        *,
        enabled_only: bool = False,
    ) -> list[SpecialistDefinitionModel]:
        if enabled_only:
            return self._repository.list_enabled()

        return self._repository.list_all()

    def get_specialist(
        self,
        specialist_id: int,
    ) -> SpecialistDefinitionModel:
        specialist = self._repository.get_by_id(
            specialist_id
        )

        if specialist is None:
            raise SpecialistDefinitionNotFoundError(
                specialist_id
            )

        return specialist

    def create_specialist(
        self,
        data: CreateSpecialistDefinitionDTO,
    ) -> SpecialistDefinitionModel:
        slug = data.slug.strip().lower()

        if self._repository.get_by_slug(slug) is not None:
            raise DuplicateSpecialistDefinitionError(
                slug
            )

        try:
            return self._repository.create(data)
        except ValueError as exc:
            if "slug already exists" in str(exc):
                raise DuplicateSpecialistDefinitionError(
                    slug
                ) from exc
            raise

    def update_specialist(
        self,
        specialist_id: int,
        data: UpdateSpecialistDefinitionDTO,
    ) -> SpecialistDefinitionModel:
        self.get_specialist(specialist_id)

        updated = self._repository.update(
            specialist_id,
            data,
        )

        if updated is None:
            raise SpecialistDefinitionNotFoundError(
                specialist_id
            )

        return updated

    def set_enabled(
        self,
        specialist_id: int,
        enabled: bool,
    ) -> SpecialistDefinitionModel:
        updated = self._repository.set_enabled(
            specialist_id,
            enabled,
        )

        if updated is None:
            raise SpecialistDefinitionNotFoundError(
                specialist_id
            )

        return updated

    def delete_specialist(
        self,
        specialist_id: int,
    ) -> None:
        if not self._repository.delete(
            specialist_id
        ):
            raise SpecialistDefinitionNotFoundError(
                specialist_id
            )
