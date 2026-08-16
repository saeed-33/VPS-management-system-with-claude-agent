"""عقود إنشاء ملفات المراقبة وتحديد الفحوص التي تنتمي إليها."""
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CreateMonitoringProfileDTO:
    """
    البيانات اللازمة لإنشاء مجموعة فحوص يمكن ربطها بسيرفر.
    """
    name: str
    description: str | None = None
    enabled: bool = True


@dataclass(slots=True, frozen=True)
class UpdateMonitoringProfileDTO:
    """
    التغييرات الاختيارية على اسم ملف المراقبة ووصفه وحالته.
    """
    name: str | None = None
    description: str | None = None
    enabled: bool | None = None


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
