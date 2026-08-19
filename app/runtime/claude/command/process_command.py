"""تعريف أمر عملية Claude."""
from dataclasses import dataclass, field
from pathlib import Path

@dataclass(slots=True, frozen=True)
class ClaudeProcessCommand:
    """
    قيمة غير قابلة للتغيير تصف البرنامج ومجلد العمل والبيئة اللازمة لتشغيل Claude.
    """
    argv: tuple[str, ...]
    cwd: Path | None = None
    env: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        يتحقق من وجود برنامج صالح في الأمر ويحول مجلد العمل إلى مسار مطلق قبل تثبيت القيمة.
        """
        if not self.argv:
            raise ValueError("Claude process argv must not be empty.")

        for item in self.argv:
            if not isinstance(item, str) or not item:
                raise ValueError(
                    "Claude process argv entries must be non-empty strings."
                )

        if self.cwd is not None:
            object.__setattr__(self, "cwd", Path(self.cwd).resolve())

