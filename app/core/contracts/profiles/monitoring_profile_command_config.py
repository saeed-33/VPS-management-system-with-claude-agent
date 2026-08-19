"""Contract class extracted from profiles.py during the structure refactor."""

from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class MonitoringProfileCommandConfig:
    """
    تعريف فحص بعد اختياره داخل ملف مراقبة.

    يثبت العقد ترتيب الفحص ومهلته وسياسة بصمة مخرجه قبل تحويله إلى نتيجة
    داخل تقرير المراقبة.
    """
    id: int
    name: str
    command: str

    timeout_seconds: float
    execution_order: int

    fingerprint_strategy: str
    fingerprint_config: dict
