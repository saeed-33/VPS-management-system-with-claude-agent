"""مكوّن دورة مراقبة السيرفر."""
from __future__ import annotations

from typing import Protocol

class ServerRecord(Protocol):
    """
    عقد يمثل الحد الأدنى من بيانات السيرفر اللازمة لدورة المراقبة.
    """
    id: int
    host: str
    port: int
    username: str

    private_key_path: str | None

    monitor_enabled: bool
    monitoring_profile_id: int | None
