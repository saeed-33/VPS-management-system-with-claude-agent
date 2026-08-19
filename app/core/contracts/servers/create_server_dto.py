"""Contract class extracted from servers.py during the structure refactor."""

from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class CreateServerDTO:
    """
    البيانات اللازمة لتسجيل سيرفر يمكن للتطبيق فحصه.

    يحدد العقد عنوان الاتصال وبيانات المستخدم ومفتاح SSH وملف المراقبة وفترة
    التكرار التي ستستخدمها الجدولة.
    """
    name: str
    host: str
    port: int
    username: str

    private_key_path: str | None = None
    description: str | None = None

    monitor_enabled: bool = True
    interval_seconds: int = 60
    monitoring_profile_id: int | None = None
