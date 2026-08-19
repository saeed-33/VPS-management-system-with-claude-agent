"""
إدارة اتصال SSH موثق إلى سيرفر مراقب.

يتحقق العميل من مفتاح الاتصال وknown_hosts، ويفتح الاتصال عند الحاجة ويغلقه
بشكل مضمون حتى تستخدم دورة المراقبة قناة آمنة ومحدودة.
"""
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType

import asyncssh


@dataclass(slots=True, frozen=True)


class SSHConnectionConfig:
    """
    إعدادات اتصال SSH تشمل هوية السيرفر ومفاتيح التحقق والمهلة.
    """
    host: str
    port: int
    username: str

    private_key_path: str
    known_hosts_path: str

    connect_timeout_seconds: float = 15.0

