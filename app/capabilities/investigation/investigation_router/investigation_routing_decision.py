"""Class extracted from investigation_router during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import re

from typing import Any, Iterable

from app.capabilities.investigation.specialist_registry.specialist_registry import SpecialistRegistry
from app.capabilities.investigation.specialist_registry.specialist_registry_snapshot import SpecialistRegistrySnapshot
from app.capabilities.investigation.specialist_registry.specialist_runtime_definition import SpecialistRuntimeDefinition

from .routing_reason import RoutingReason

from .specialist_routing_match import SpecialistRoutingMatch

@dataclass(slots=True, frozen=True)
class InvestigationRoutingDecision:
    """
    يمثل قرار توجيه التقرير وقائمة المرشحين والاختصاصيين المختارين.
    """
    should_investigate: bool
    reasons: tuple[RoutingReason, ...]
    detected_domains: tuple[str, ...]
    candidate_specialists: tuple[SpecialistRoutingMatch, ...]
    selected_specialists: tuple[SpecialistRoutingMatch, ...]
    unmatched_issue_indexes: tuple[int, ...]
    registry_size: int
    candidate_limit: int
    selection_limit: int

    @property
    def candidate_slugs(self) -> tuple[str, ...]:
        """
        ينفذ عملية candidate slugs ضمن دورة التحقيق وجمع الأدلة.
        """
        return tuple(x.specialist_slug for x in self.candidate_specialists)

    @property
    def selected_slugs(self) -> tuple[str, ...]:
        """
        ينفذ عملية selected slugs ضمن دورة التحقيق وجمع الأدلة.
        """
        return tuple(x.specialist_slug for x in self.selected_specialists)
