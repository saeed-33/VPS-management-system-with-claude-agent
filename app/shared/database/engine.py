"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.engine import (
    create_database_tables,
    engine,
)

__all__ = [
    "create_database_tables",
    "engine",
]
