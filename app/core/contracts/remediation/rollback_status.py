"""Contract class extracted from remediation.py during the structure refactor."""

from __future__ import annotations

import hashlib

import json

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

class RollbackStatus(StrEnum):
    """
    حالات التراجع عندما لا يثبت التحقق نجاح المعالجة.
    """
    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
