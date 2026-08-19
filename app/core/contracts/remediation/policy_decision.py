"""Contract class extracted from remediation.py during the structure refactor."""

from __future__ import annotations

import hashlib

import json

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

class PolicyDecision(StrEnum):
    """
    مآل فحص سياسة المعالجة قبل السماح بالانتقال التالي.
    """
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    REQUIRE_ADDITIONAL_VALIDATION = "require_additional_validation"
