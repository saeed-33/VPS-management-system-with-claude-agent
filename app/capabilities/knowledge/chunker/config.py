"""إعدادات تقطيع وثائق المعرفة."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class KnowledgeChunkerConfig:
    """
    يضبط أحجام المقاطع والتداخل والحد الأدنى مع التحقق من أن الحدود متسقة.
    """
    target_chars: int = 1800
    max_chars: int = 2600
    overlap_chars: int = 240
    min_chars: int = 180

    def __post_init__(self) -> None:
        """
        يتحقق من أن أهداف حجم المقطع والتداخل والحد الأدنى قابلة للتطبيق.
        """
        if self.target_chars < 200:
            raise ValueError("target_chars must be >= 200.")
        if self.max_chars < self.target_chars:
            raise ValueError("max_chars must be >= target_chars.")
        if self.overlap_chars < 0:
            raise ValueError("overlap_chars must be >= 0.")
        if self.overlap_chars >= self.target_chars:
            raise ValueError("overlap_chars must be < target_chars.")
        if self.min_chars < 1:
            raise ValueError("min_chars must be >= 1.")
