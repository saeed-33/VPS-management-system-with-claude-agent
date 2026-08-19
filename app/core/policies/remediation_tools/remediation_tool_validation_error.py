"""Class extracted from remediation_tools during the structure refactor."""

from __future__ import annotations

import re

from dataclasses import dataclass

from typing import Any

from app.core.contracts.remediation.remediation_action import RemediationAction
from app.core.contracts.remediation.remediation_risk import RemediationRisk

class RemediationToolValidationError(ValueError):
    """
    خطأ يوضح أن فعل تغيير أو هدفه لا يطابق قائمة الأفعال المسموحة.
    """
    pass
