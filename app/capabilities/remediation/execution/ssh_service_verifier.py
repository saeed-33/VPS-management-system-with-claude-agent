"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

from app.core.contracts.remediation.remediation_action import RemediationAction
from .ssh_named_command_runner import _SSHNamedCommandRunner

class SSHServiceVerifier(_SSHNamedCommandRunner):
    """
    يتحقق عبر SSH من أثر تغيير خدمة، بما في ذلك حالتها المتوقعة.
    """
    def verify(self, *, server_id: int, action: RemediationAction) -> tuple[bool, dict]:
        """
        ينفذ فحص الخدمة عبر SSH ويعيد نتيجة التحقق من أثر التغيير.
        """
        return self.verify_state(
            server_id=server_id,
            service=action.target,
            expected_state="active",
        )

    def verify_state(self, *, server_id: int, service: str, expected_state: str) -> tuple[bool, dict]:
        """
        يقرأ حالة الخدمة عبر SSH ويقارنها بالحالة المتوقعة.
        """
        # وصل الهدف بعد اجتياز قائمة التغيير المسموح بها؛ وفحص القراءة ثابت
        # ولا يقبل نص أوامر من خارج السجل.
        result = self._run_sync(lambda: self._execute(
            server_id=server_id,
            command=f"systemctl is-active {service}",
            command_name="verify_service_state",
            timeout=30.0,
        ))
        observed = result.stdout.strip()
        return observed == expected_state, {
            "expected": expected_state,
            "observed": observed,
            "exit_status": result.exit_status,
            "error": result.error,
        }
