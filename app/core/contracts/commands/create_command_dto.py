"""Contract class extracted from commands.py during the structure refactor."""

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
    # الافتراضي يقلل الضوضاء في الأوامر متعددة الأسطر.
    fingerprint_strategy: str = "canonical_lines"
    fingerprint_config: dict = field(
        default_factory=dict
    )
    description: str | None = None
    timeout_seconds: float = 20.0
    enabled: bool = True
