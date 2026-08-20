"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

from .write_command_result import WriteCommandResult

class UnavailableWriteRunner:
    """
    يمثل منفذ كتابة غير متاح ويعيد فشلًا صريحًا بدل تنفيذ وهمي.
    """
    def run(self, **_kwargs) -> WriteCommandResult:
        """
        يعيد نتيجة فشل توضّح أن تنفيذ الكتابة غير متاح.
        """
        return WriteCommandResult(success=False, error="safe_write_runner_not_configured")
