"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.session import (
    SessionLocal,
    get_database_session,
)

__all__ = [
    "SessionLocal",
    "get_database_session",
]
