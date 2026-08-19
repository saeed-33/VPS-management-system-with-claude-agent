"""Class extracted from diagnostic_tools during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import ipaddress

import re

import shlex

from types import MappingProxyType

from typing import Any, Mapping

@dataclass(slots=True, frozen=True)
class DiagnosticToolCall:
    """
    طلب أداة تشخيص ومعاملاتها قبل تمريرها إلى السياسة.
    """
    tool_id: str
    arguments: Mapping[str, Any]
