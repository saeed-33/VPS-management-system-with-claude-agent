"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class WriteCommandResult:
    """
    يمثل نتيجة تنفيذ أمر كتابة مع الخروج والمخرجات والمدة ورسالة الخطأ.
    """
    success: bool
    exit_status: int | None = None
    stdout: str = ""
    stderr: str = ""
    error: str | None = None
