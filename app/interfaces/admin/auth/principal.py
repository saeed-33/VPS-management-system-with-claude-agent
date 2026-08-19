"""هوية المستخدم الإداري وصلاحياته."""
from __future__ import annotations

from dataclasses import dataclass

from app.infrastructure.database.models.admin_auth.user import AdminUserModel

from .permissions import AdminPermission, AdminRole, ROLE_PERMISSIONS


@dataclass(frozen=True, slots=True)
class AdminPrincipal:
    """
    يمثل هوية المستخدم الإداري وصلاحياته المرتبطة بالطلب الحالي.
    """

    user_id: int
    username: str
    role: AdminRole
    permissions: frozenset[AdminPermission]

    def can(self, permission: str | AdminPermission) -> bool:
        """
        يتحقق من امتلاك الهوية لصلاحية إدارية محددة.
        """
        return AdminPermission(permission) in self.permissions


def principal_from_model(model: AdminUserModel) -> AdminPrincipal:
    """
    يحوّل نموذج المستخدم الإداري إلى هوية تحمل الدور والصلاحيات المطَبّعة.
    """
    role = AdminRole(model.role)
    return AdminPrincipal(
        user_id=model.id,
        username=model.username,
        role=role,
        permissions=ROLE_PERMISSIONS[role],
    )
