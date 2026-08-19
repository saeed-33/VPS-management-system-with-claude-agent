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

SERVICE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.@-]{0,127}$")
