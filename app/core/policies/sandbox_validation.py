from __future__ import annotations

from app.core.contracts.sandbox_validation import SandboxTarget
from app.core.policies.remediation_tools import SERVICE_NAME_RE


SAFE_MARKERS = ("safe-remediation-test", "non-production")


def validate_sandbox_target(*, server, target: SandboxTarget) -> None:
    if server is None or server.id != target.server_id or server.name != target.server_name:
        raise ValueError("Sandbox target identity does not match the registered server.")
    if not SERVICE_NAME_RE.fullmatch(target.service):
        raise ValueError("Sandbox service is not a valid registered service identifier.")
    designation = (server.description or "").casefold()
    if any(marker not in designation for marker in SAFE_MARKERS):
        raise ValueError("Sandbox target is not explicitly designated safe and non-production.")
    if "production" in designation and "non-production" not in designation:
        raise ValueError("Production targets cannot be used for sandbox validation.")
