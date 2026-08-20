"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

from typing import Protocol

from app.core.contracts.remediation.remediation_action import RemediationAction
from app.core.contracts.remediation.write_command_result import WriteCommandResult

class WriteCommandRunner(Protocol):
    """
    يعرّف عقد تشغيل أمر تغيير على السيرفر.
    """
    def run(self, *, server_id: int, action: RemediationAction, command: str, timeout_seconds: float) -> WriteCommandResult:
        """
        يعرّف عملية تشغيل أمر كتابة على السيرفر المستهدف.
        """
        ...
