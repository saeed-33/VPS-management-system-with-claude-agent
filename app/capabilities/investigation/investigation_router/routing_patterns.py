"""
توجيه تقرير المراقبة إلى الاختصاصيين المناسبين.

يستخرج إشارات الصحة والأخطاء والقضايا القابلة للفعل، يطابقها مع مجالات
الاختصاصيين، ثم يعيد قرار توجيه مفسرًا وقابلًا للتتبع.
"""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import re

from typing import Any, Iterable

from app.capabilities.investigation.specialist_registry.specialist_registry import SpecialistRegistry
from app.capabilities.investigation.specialist_registry.specialist_registry_snapshot import SpecialistRegistrySnapshot
from app.capabilities.investigation.specialist_registry.specialist_runtime_definition import SpecialistRuntimeDefinition

_SPACE_RE = re.compile(r"\s+")

_BOUNDARY_RE = re.compile(r"[^\w]+", re.UNICODE)
