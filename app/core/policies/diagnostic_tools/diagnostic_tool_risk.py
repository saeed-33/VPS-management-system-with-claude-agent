"""Class extracted from diagnostic_tools during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass

from enum import StrEnum

import ipaddress

import re

import shlex

from types import MappingProxyType

from typing import Any, Mapping

class DiagnosticToolRisk(StrEnum):
    """
    مستويات الأثر المسموحة لأدوات التشخيص، والمجموعة الحالية للقراءة فقط.
    """
    READ_ONLY = "read_only"
