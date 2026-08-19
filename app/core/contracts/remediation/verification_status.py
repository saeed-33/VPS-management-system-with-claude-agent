"""Contract class extracted from remediation.py during the structure refactor."""

from __future__ import annotations

import hashlib

import json

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

class VerificationStatus(StrEnum):
    """
    نتيجة فحص حالة السيرفر بعد تطبيق التغيير.
    """
    VERIFIED = "verified"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"
