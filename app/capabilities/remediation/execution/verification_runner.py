"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

from typing import Protocol

from app.core.contracts.remediation.remediation_action import RemediationAction

class VerificationRunner(Protocol):
    """
    يعرّف عقد التحقق من أثر التغيير بعد التنفيذ.
    """
    def verify(self, *, server_id: int, action: RemediationAction) -> tuple[bool, dict]:
        """
        يعرّف عملية التحقق من أثر التغيير بعد تشغيله.
        """
        ...
