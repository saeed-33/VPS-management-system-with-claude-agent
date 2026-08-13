from __future__ import annotations

from app.infrastructure.database.repositories.knowledge_source_repository import (
    KnowledgeSourceRepository,
)
from app.core.contracts.knowledge_sources import (
    CreateKnowledgeSourceDTO,
    UpdateKnowledgeSourceDTO,
)


class KnowledgeSourceService:
    def __init__(
        self,
        repository: KnowledgeSourceRepository,
    ) -> None:
        self._repository = repository

    def list_sources(
        self,
        *,
        enabled_only: bool = False,
    ):
        if enabled_only:
            return (
                self._repository
                .list_enabled()
            )

        return self._repository.list_all()

    def get_source(
        self,
        source_id: int,
    ):
        source = self._repository.get_by_id(
            source_id
        )

        if source is None:
            raise LookupError(
                "Knowledge source not found."
            )

        return source

    def create_source(
        self,
        data: CreateKnowledgeSourceDTO,
    ):
        return self._repository.create(data)

    def update_source(
        self,
        source_id: int,
        data: UpdateKnowledgeSourceDTO,
    ):
        source = self._repository.update(
            source_id,
            data,
        )

        if source is None:
            raise LookupError(
                "Knowledge source not found."
            )

        return source

    def set_enabled(
        self,
        source_id: int,
        enabled: bool,
    ):
        source = (
            self._repository
            .set_enabled(
                source_id,
                enabled,
            )
        )

        if source is None:
            raise LookupError(
                "Knowledge source not found."
            )

        return source

    def delete_source(
        self,
        source_id: int,
    ) -> None:
        if not self._repository.delete(
            source_id
        ):
            raise LookupError(
                "Knowledge source not found."
            )
