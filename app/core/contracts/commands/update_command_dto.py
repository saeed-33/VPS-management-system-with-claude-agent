"""Contract class extracted from commands.py during the structure refactor."""

from dataclasses import dataclass, field

@dataclass(slots=True, frozen=True)
class UpdateCommandDTO:
    """
    التغييرات الاختيارية التي يمكن تطبيقها على فحص مراقبة مسجل.

    تمثل القيم الفارغة عدم تغيير الحقل، بينما تسمح القيم المحددة بتعديل اسم
    الفحص أو نصه أو مهلة تنفيذه أو سياسة بصمته.
    """
    name: str | None = None
    command: str | None = None

    description: str | None = None
    timeout_seconds: float | None = None
    enabled: bool | None = None
    fingerprint_strategy: str | None = None
    fingerprint_config: dict | None = None
