"""Contract class extracted from commands.py during the structure refactor."""

from dataclasses import dataclass, field

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
