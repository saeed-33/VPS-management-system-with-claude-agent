"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.investigation_repository import (
    InvestigationRepository,
)

__all__ = [
    "InvestigationRepository",
]
