"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.analysis_source_repository import (
    AnalysisSourceRepository,
)

__all__ = [
    "AnalysisSourceRepository",
]
