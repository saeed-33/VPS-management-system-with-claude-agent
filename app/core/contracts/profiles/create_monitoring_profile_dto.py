"""Contract class extracted from profiles.py during the structure refactor."""

from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class CreateMonitoringProfileDTO:
    """
    البيانات اللازمة لإنشاء مجموعة فحوص يمكن ربطها بسيرفر.
    """
    name: str
    description: str | None = None
    enabled: bool = True
