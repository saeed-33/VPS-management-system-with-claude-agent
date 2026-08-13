"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.command_repository import (
    CommandRepository,
)

__all__ = [
    "CommandRepository",
]
