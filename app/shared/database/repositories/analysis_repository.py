"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.analysis_repository import (
    AnalysisRepository,
)

__all__ = [
    "AnalysisRepository",
]
