"""أدوار مستخدمي الإدارة."""

from enum import StrEnum


class AdminRole(StrEnum):
    """يمثل أدوار المستخدمين الإداريين."""

    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"
