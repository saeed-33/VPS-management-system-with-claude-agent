"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

from app.core.contracts.remediation.remediation_action import RemediationAction
from .ssh_named_command_runner import _SSHNamedCommandRunner
from .write_command_result import WriteCommandResult

class SSHNamedWriteRunner(_SSHNamedCommandRunner):
    """
    ينفذ أمر كتابة مسمى عبر SSH ويحوّل النتيجة إلى عقد نتيجة الكتابة.
    """
    def run(self, *, server_id: int, action: RemediationAction, command: str, timeout_seconds: float) -> WriteCommandResult:
        """
        ينفذ أمر الكتابة المسمى عبر SSH ويعيد مخرجاته ومدة تشغيله.
        """
        return self._run_sync(lambda: self._execute(
            server_id=server_id, command=command, command_name=action.action_type, timeout=timeout_seconds
        ))
