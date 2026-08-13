"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.remediation_repository import (
    RemediationRepository,
)

__all__ = [
    "RemediationRepository",
]
