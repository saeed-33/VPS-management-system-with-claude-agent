"""Contract class extracted from sandbox_validation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

@dataclass(frozen=True, slots=True)
class SandboxTarget:
    """
    هوية السيرفر والخدمة التي ستختبر الخطة أثرها عليهما.
    """
    server_id: int
    server_name: str
    service: str
    designation: str

    def __post_init__(self) -> None:
        """يتحقق من أن هدف الاختبار يملك سيرفرًا وخدمة معروفين."""
        if self.server_id < 1 or not self.server_name.strip() or not self.service.strip():
            raise ValueError("Sandbox target identity is incomplete.")
