"""Connection settings passed from monitoring capabilities to an SSH adapter."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MonitoringConnectionConfig:
    """Transport-neutral connection settings for monitoring execution."""

    host: str
    port: int
    username: str
    private_key_path: str
    known_hosts_path: str
    connect_timeout_seconds: float

