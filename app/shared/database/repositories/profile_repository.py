"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.profile_repository import (
    MonitoringProfileRepository,
)

__all__ = [
    "MonitoringProfileRepository",
]
