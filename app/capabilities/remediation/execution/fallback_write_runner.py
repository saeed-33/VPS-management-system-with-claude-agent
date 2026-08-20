"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

from app.core.contracts.remediation.write_command_result import WriteCommandResult

class FallbackWriteRunner:
    """
    يمثل منفذ كتابة احتياطياً يعيد فشلاً صريحاً بدل تنفيذ وهمي.
    """
    def run(self, **_kwargs) -> WriteCommandResult:
        """
        يعيد نتيجة فشل توضّح أن تنفيذ الكتابة غير متاح.
        """
        return WriteCommandResult(success=False, error="safe_write_runner_not_configured")
