"""Class extracted from investigation_router during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import re

from typing import Any, Iterable

from app.capabilities.investigation.specialist_registry.specialist_registry import SpecialistRegistry
from app.capabilities.investigation.specialist_registry.specialist_registry_snapshot import SpecialistRegistrySnapshot
from app.capabilities.investigation.specialist_registry.specialist_runtime_definition import SpecialistRuntimeDefinition

@dataclass(slots=True, frozen=True)
class SpecialistRoutingMatch:
    """
    يمثل مطابقة اختصاصي مع إشارات التقرير ودرجة التغطية.
    """
    specialist_id: int
    specialist_slug: str
    specialist_name: str
    score: int
    matched_domains: tuple[str, ...]
    matched_trigger_hints: tuple[str, ...]
    matched_issue_indexes: tuple[int, ...]
    priority: int
