"""Contract class extracted from remediation.py during the structure refactor."""

from __future__ import annotations

import hashlib

import json

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

class RemediationPlanStatus(StrEnum):
    """
    انتقالات خطة المعالجة من الاقتراح حتى النجاح أو الفشل أو التراجع.
    """
    PROPOSED = "proposed"
    SANDBOX_PASSED = "sandbox_passed"
    SANDBOX_FAILED = "sandbox_failed"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    VERIFICATION_PENDING = "verification_pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLBACK_REQUIRED = "rollback_required"
    ROLLBACK_SUCCEEDED = "rollback_succeeded"
    ROLLBACK_FAILED = "rollback_failed"
    CANCELLED = "cancelled"
    NO_SOLUTION_FOUND = "no_solution_found"
    APPLIED = "applied"  # historical terminal value
    BLOCKED = "blocked"
