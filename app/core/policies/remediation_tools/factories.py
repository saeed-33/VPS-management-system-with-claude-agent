"""
قائمة أفعال التغيير المسموحة وأهداف خدماتها.

لا تسمح هذه الوحدة إلا بأفعال مسماة مثل بدء خدمة أو إيقافها، وتتحقق من اسم
الخدمة والمعاملات قبل توليد أمر systemctl ثابت.
"""

from __future__ import annotations

import re

from dataclasses import dataclass

from typing import Any

from app.core.contracts.remediation.remediation_action import RemediationAction
from app.core.contracts.remediation.remediation_risk import RemediationRisk

from .named_write_tool import NamedWriteTool

from .named_write_tool_registry import NamedWriteToolRegistry

from .remediation_tool_validation_error import RemediationToolValidationError

def build_default_write_tool_registry() -> NamedWriteToolRegistry:
    """
    يبني القائمة القياسية لأفعال الخدمات المسموحة ومستويات خطرها وإمكان التراجع.
    """
    return NamedWriteToolRegistry(
        (
            # الفعل الآلي الوحيد هنا أداة مسماة منخفضة الخطر ومذكورة صراحة في
            # القائمة المسموحة.
            NamedWriteTool("start_service", RemediationRisk.LOW.value, 30.0, "stop_service", "active"),
            NamedWriteTool("stop_service", RemediationRisk.HIGH.value, 30.0, "start_service", "inactive"),
            # تكرار إعادة التشغيل أو التحميل لا يعيد الحالة السابقة؛ لذلك لا
            # نعد بدعم التراجع حتى تتوفر استعادة حقيقية للعملية والإعدادات.
            NamedWriteTool("restart_service", RemediationRisk.HIGH.value, 45.0, None, "active"),
            NamedWriteTool("reload_service", RemediationRisk.MEDIUM.value, 30.0, None, "active"),
        )
    )

def action_from_tool_arguments(arguments: dict[str, Any]) -> RemediationAction:
    """
    يحول معاملات طلب أداة المعالجة إلى فعل مسمى يخضع لبقية التحققات.
    """
    action_type = arguments.get("action_type") or arguments.get("tool")
    if not isinstance(action_type, str) or not action_type.strip():
        raise RemediationToolValidationError("action_type is required.")
    target = arguments.get("target") or arguments.get("service")
    if not isinstance(target, str) or not target.strip():
        raise RemediationToolValidationError("target is required.")
    return RemediationAction(
        action_type=action_type,
        target=target,
        parameters=dict(arguments.get("parameters") or {}),
        reason=str(arguments.get("reason") or ""),
        expected_effect=str(arguments.get("expected_effect") or ""),
        action_id=str(arguments.get("action_id") or action_type),
    )
