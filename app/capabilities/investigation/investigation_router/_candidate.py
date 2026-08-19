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
class _Candidate:
    """
    يمثل مرشح اختصاصي أثناء حساب قرار التوجيه.
    """
    specialist: SpecialistRuntimeDefinition
    score: int
    matched_domains: tuple[str, ...]
    matched_trigger_hints: tuple[str, ...]
    matched_issue_indexes: tuple[int, ...]
