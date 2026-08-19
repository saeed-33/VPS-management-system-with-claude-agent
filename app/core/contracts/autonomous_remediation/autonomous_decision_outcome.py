"""Contract class extracted from autonomous_remediation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

class AutonomousDecisionOutcome(StrEnum):
    """
    النتيجة العملية لتقييم أهلية المعالجة الذاتية.
    """
    AUTO_EXECUTE = "auto_execute"
    REQUIRE_HUMAN_APPROVAL = "require_human_approval"
    DENY = "deny"
