"""Class extracted from investigation_router during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import re

from typing import Any, Iterable

from app.capabilities.investigation.specialist_registry.specialist_registry import SpecialistRegistry
from app.capabilities.investigation.specialist_registry.specialist_registry_snapshot import SpecialistRegistrySnapshot
from app.capabilities.investigation.specialist_registry.specialist_runtime_definition import SpecialistRuntimeDefinition

class RoutingReason(StrEnum):
    """
    يمثل سبب اختيار أو استبعاد اختصاصي في قرار التوجيه.
    """
    ANALYSIS_ISSUES = "analysis_issues"
    ANALYSIS_HEALTH = "analysis_health"
    REPORT_FAILURE = "report_failure"
    HEALTHY_NO_ISSUES = "healthy_no_issues"
    NO_ACTIONABLE_SIGNAL = "no_actionable_signal"
    NO_SUITABLE_SPECIALIST = "no_suitable_specialist"
