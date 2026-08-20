"""Provider-neutral server data required by investigation capabilities."""

from __future__ import annotations

from typing import Protocol


class InvestigationServerRecord(Protocol):
    """
    يصف بيانات السيرفر اللازمة لتوجيه جمع الدليل.
    """
    id: int
    host: str
    port: int
    username: str
    private_key_path: str | None
