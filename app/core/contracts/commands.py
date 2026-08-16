"""عقود تعريف فحوص المراقبة وتحديد كيفية تنفيذها على السيرفر."""
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CreateCommandDTO:
    """
    البيانات المطلوبة لتسجيل فحص جديد يمكن لملف المراقبة تشغيله.

    يجمع العقد نص الفحص وحده الزمني وطريقة بصم مخرجه، حتى يمكن مقارنة النتائج
    الحالية بالسابقة دون فقدان تعريف الفحص الذي أنتجها.
    """
    name: str
    command: str
    fingerprint_strategy: str = "full_output"
    fingerprint_config: dict = field(
        default_factory=dict
    )
    description: str | None = None
    timeout_seconds: float = 20.0
    enabled: bool = True


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


@dataclass(slots=True, frozen=True)
class CommandExecutionConfig:
    """
    نسخة تنفيذية من فحص اختاره ملف مراقبة لسيرفر محدد.

    يضيف العقد ترتيب التنفيذ والمهلة إلى تعريف الفحص حتى تنفذ دورة المراقبة
    الخطوات بالترتيب المسجل.
    """
    id: int
    name: str
    command: str

    timeout_seconds: float
    execution_order: int
