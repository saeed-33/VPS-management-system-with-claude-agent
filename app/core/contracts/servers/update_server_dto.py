"""Contract class extracted from servers.py during the structure refactor."""

from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class UpdateServerDTO:
    """
    التغييرات الاختيارية على تعريف السيرفر وإعدادات مراقبته.

    يسمح العقد بتعديل الاتصال أو تفعيل المراقبة أو تبديل ملفها دون إعادة إنشاء
    سجل السيرفر أو فقدان تقاريره السابقة.
    """
    name: str | None = None
    host: str | None = None
    port: int | None = None
    username: str | None = None

    private_key_path: str | None = None
    description: str | None = None

    monitor_enabled: bool | None = None
    interval_seconds: int | None = None
    monitoring_profile_id: int | None = None
