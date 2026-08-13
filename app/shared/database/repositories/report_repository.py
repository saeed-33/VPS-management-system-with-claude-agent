"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.report_repository import (
    ReportRepository,
)

__all__ = [
    "ReportRepository",
]
