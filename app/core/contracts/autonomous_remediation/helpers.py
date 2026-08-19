"""عقود قرار المعالجة الذاتية وحدود السماح بتنفيذها على السيرفر."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

V1_AUTONOMOUS_ACTIONS = frozenset({"start_service"})

V1_AUTONOMOUS_RISK_CEILING = "low"
