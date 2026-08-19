"""Contract class extracted from profiles.py during the structure refactor."""

from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class UpdateMonitoringProfileDTO:
    """
    التغييرات الاختيارية على اسم ملف المراقبة ووصفه وحالته.
    """
    name: str | None = None
    description: str | None = None
    enabled: bool | None = None
