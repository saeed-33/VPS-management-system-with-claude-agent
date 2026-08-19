"""أدوار وصلاحيات واجهة الإدارة."""
from __future__ import annotations

from enum import StrEnum

from .role import AdminRole


class AdminPermission(StrEnum):
    """
    يمثل الصلاحيات الدقيقة التي تحمي عمليات القراءة والكتابة والموافقة والتنفيذ.
    """
    ADMIN_READ = "admin.read"
    SERVER_READ = "server.read"
    SERVER_WRITE = "server.write"
    PROFILE_READ = "profile.read"
    PROFILE_WRITE = "profile.write"
    MONITORING_READ = "monitoring.read"
    MONITORING_CONTROL = "monitoring.control"
    COMMAND_READ = "command.read"
    COMMAND_WRITE = "command.write"
    INVESTIGATION_READ = "investigation.read"
    REPORT_READ = "report.read"
    SPECIALIST_READ = "specialist.read"
    SPECIALIST_WRITE = "specialist.write"
    KNOWLEDGE_READ = "knowledge.read"
    KNOWLEDGE_WRITE = "knowledge.write"
    REMEDIATION_READ = "remediation.read"
    REMEDIATION_APPROVE = "remediation.approve"
    REMEDIATION_EXECUTE = "remediation.execute"
    REMEDIATION_ROLLBACK = "remediation.rollback"
    AUTONOMOUS_READ = "autonomous.read"
    AUTONOMOUS_POLICY_CREATE = "autonomous.policy.create"
    AUTONOMOUS_POLICY_UPDATE = "autonomous.policy.update"
    AUTONOMOUS_POLICY_ENABLE = "autonomous.policy.enable"
    AUTONOMOUS_POLICY_DISABLE = "autonomous.policy.disable"
    AUTONOMOUS_POLICY_SUSPEND = "autonomous.policy.suspend"
    AUTONOMOUS_POLICY_RESUME = "autonomous.policy.resume"
    AUDIT_READ = "audit.read"
    SYSTEM_READ = "system.read"
    SYSTEM_ADMIN = "system.admin"


_READ_PERMISSIONS = frozenset(
    {
        AdminPermission.ADMIN_READ,
        AdminPermission.SERVER_READ,
        AdminPermission.PROFILE_READ,
        AdminPermission.MONITORING_READ,
        AdminPermission.COMMAND_READ,
        AdminPermission.INVESTIGATION_READ,
        AdminPermission.REPORT_READ,
        AdminPermission.SPECIALIST_READ,
        AdminPermission.KNOWLEDGE_READ,
        AdminPermission.REMEDIATION_READ,
        AdminPermission.AUTONOMOUS_READ,
        AdminPermission.AUDIT_READ,
        AdminPermission.SYSTEM_READ,
    }
)


_OPERATOR_PERMISSIONS = frozenset(
    {
        AdminPermission.MONITORING_CONTROL,
        AdminPermission.REMEDIATION_APPROVE,
        AdminPermission.REMEDIATION_EXECUTE,
        AdminPermission.REMEDIATION_ROLLBACK,
    }
)


_ADMIN_PERMISSIONS = frozenset(
    {
        AdminPermission.SERVER_WRITE,
        AdminPermission.PROFILE_WRITE,
        AdminPermission.COMMAND_WRITE,
        AdminPermission.SPECIALIST_WRITE,
        AdminPermission.KNOWLEDGE_WRITE,
        AdminPermission.AUTONOMOUS_POLICY_CREATE,
        AdminPermission.AUTONOMOUS_POLICY_UPDATE,
        AdminPermission.AUTONOMOUS_POLICY_ENABLE,
        AdminPermission.AUTONOMOUS_POLICY_DISABLE,
        AdminPermission.AUTONOMOUS_POLICY_SUSPEND,
        AdminPermission.AUTONOMOUS_POLICY_RESUME,
        AdminPermission.SYSTEM_ADMIN,
    }
)


ROLE_PERMISSIONS: dict[AdminRole, frozenset[AdminPermission]] = {
    AdminRole.VIEWER: _READ_PERMISSIONS,
    AdminRole.OPERATOR: _READ_PERMISSIONS | _OPERATOR_PERMISSIONS,
    AdminRole.ADMIN: _READ_PERMISSIONS | _OPERATOR_PERMISSIONS | _ADMIN_PERMISSIONS,
}


def permission_for_api_request(
    method: str, path: str, *, payload: object | None = None
) -> AdminPermission:
    """
    يحدد الصلاحية المطلوبة لطلب API الإداري من مساره وطريقة HTTP.
    """
    normalized = path.rstrip("/") or "/"
    if normalized.startswith("/api/servers"):
        if normalized.endswith("/test"):
            return AdminPermission.MONITORING_CONTROL
        if (
            method == "PATCH"
            and isinstance(payload, dict)
            and set(payload) == {"monitor_enabled"}
        ):
            return AdminPermission.MONITORING_CONTROL
        return AdminPermission.SERVER_READ if method == "GET" else AdminPermission.SERVER_WRITE
    if normalized.startswith("/api/commands"):
        return AdminPermission.COMMAND_READ if method == "GET" else AdminPermission.COMMAND_WRITE
    if normalized.startswith("/api/monitoring-profiles"):
        return AdminPermission.PROFILE_READ if method == "GET" else AdminPermission.PROFILE_WRITE
    if normalized.startswith("/api/reports"):
        return AdminPermission.REPORT_READ
    if normalized.startswith("/api/investigations"):
        return AdminPermission.INVESTIGATION_READ
    if normalized.startswith("/api/diagnostic-tools"):
        return AdminPermission.SYSTEM_READ
    if normalized.startswith("/api/specialists"):
        return AdminPermission.SPECIALIST_READ if method == "GET" else AdminPermission.SPECIALIST_WRITE
    if normalized.startswith("/api/knowledge-sources"):
        return AdminPermission.KNOWLEDGE_READ if method == "GET" else AdminPermission.KNOWLEDGE_WRITE
    if normalized.startswith("/api/agent-observability"):
        return AdminPermission.SYSTEM_READ
    if normalized == "/api/system/runtime":
        return AdminPermission.SYSTEM_READ
    if normalized.startswith("/api/remediation"):
        if method == "GET":
            return AdminPermission.REMEDIATION_READ
        if "/approval" in normalized:
            return AdminPermission.REMEDIATION_APPROVE
        if normalized.endswith("/execute"):
            return AdminPermission.REMEDIATION_EXECUTE
        if normalized.endswith("/rollback"):
            return AdminPermission.REMEDIATION_ROLLBACK
        return AdminPermission.REMEDIATION_APPROVE
    if normalized.startswith("/api/autonomous-remediation"):
        if method == "GET":
            if normalized.startswith("/api/autonomous-remediation/audit"):
                return AdminPermission.AUDIT_READ
            return AdminPermission.AUTONOMOUS_READ
        if normalized.endswith("/enable"):
            return AdminPermission.AUTONOMOUS_POLICY_ENABLE
        if normalized.endswith("/disable"):
            return AdminPermission.AUTONOMOUS_POLICY_DISABLE
        if normalized.endswith("/suspend"):
            return AdminPermission.AUTONOMOUS_POLICY_SUSPEND
        if normalized.endswith("/resume"):
            return AdminPermission.AUTONOMOUS_POLICY_RESUME
        if method == "POST":
            return AdminPermission.AUTONOMOUS_POLICY_CREATE
        return AdminPermission.AUTONOMOUS_POLICY_UPDATE
    return AdminPermission.SYSTEM_ADMIN if method != "GET" else AdminPermission.ADMIN_READ
