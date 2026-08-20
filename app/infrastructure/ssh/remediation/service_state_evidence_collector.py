"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

from .service_state_observation import ServiceStateObservation
from .ssh_named_command_runner import _SSHNamedCommandRunner


class SSHServiceStateEvidenceCollector(_SSHNamedCommandRunner):
    """
    يجمع حالة خدمة وأدلتها عبر SSH من السيرفر المستهدف.
    """
    def collect(self, *, server_id: int, service: str) -> ServiceStateObservation:
        """
        يجمع ملاحظة حالة الخدمة ومخرجاتها عبر SSH لتوثيق الدليل.
        """
        # يجمع الدليل باسم خدمة تم التحقق منه عبر أداة المعالجة المسجلة، ولا
        # يحول إدخال المستخدم إلى نص أوامر قابل للتنفيذ.
        result = self._run_sync(lambda: self._execute(
            server_id=server_id,
            command=f"systemctl is-active {service}",
            command_name="collect_remediation_service_state",
            timeout=30.0,
        ))
        state = result.stdout.strip()
        if state not in {"active", "inactive", "failed", "activating", "deactivating"}:
            state = "unknown"
        return ServiceStateObservation(
            state=state,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_status=result.exit_status,
            error=result.error,
            metadata={"command_name": "collect_remediation_service_state"},
        )
