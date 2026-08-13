"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)

__all__ = [
    "SpecialistDefinitionRepository",
]
