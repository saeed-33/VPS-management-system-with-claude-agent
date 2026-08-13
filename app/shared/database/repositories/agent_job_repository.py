"""Compatibility facade for relocated database implementation."""

from app.infrastructure.database.repositories.agent_job_repository import (
    AgentJobRepository,
)

__all__ = [
    "AgentJobRepository",
]
