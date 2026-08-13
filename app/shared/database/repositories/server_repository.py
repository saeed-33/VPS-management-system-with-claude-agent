"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.server_repository import (
    ServerRepository,
)

__all__ = [
    "ServerRepository",
]
