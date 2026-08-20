"""Connection settings passed from investigation capabilities to an SSH adapter."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DiagnosticConnectionConfig:
    """Transport-neutral connection settings for diagnostic execution."""

    host: str
    port: int
    username: str
    private_key_path: str
    known_hosts_path: str
    connect_timeout_seconds: float

