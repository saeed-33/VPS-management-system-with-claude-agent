"""Contract class extracted from autonomous_remediation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

from typing import Any

class AutonomousDecisionReasonCode(StrEnum):
    """
    رموز تشرح لماذا سمحت السياسة بالمعالجة أو طلبت موافقة أو منعتها.
    """
    POLICY_MATCH = "policy_match"
    POLICY_DISABLED = "policy_disabled"
    POLICY_SUSPENDED = "policy_suspended"
    GLOBAL_AUTONOMY_DISABLED = "global_autonomy_disabled"
    ACTION_NOT_AUTONOMOUS_ALLOWLISTED = "action_not_autonomous_allowlisted"
    TARGET_NOT_ALLOWED = "target_not_allowed"
    SERVER_NOT_ALLOWED = "server_not_allowed"
    RISK_TOO_HIGH = "risk_too_high"
    CONFIDENCE_INSUFFICIENT = "confidence_insufficient"
    EVIDENCE_INCOMPLETE = "evidence_incomplete"
    HISTORICAL_SUCCESSES_INSUFFICIENT = "historical_successes_insufficient"
    HISTORICAL_FAILURE_RATE_TOO_HIGH = "historical_failure_rate_too_high"
    SANDBOX_MISSING = "sandbox_missing"
    SANDBOX_FAILED = "sandbox_failed"
    SANDBOX_STALE = "sandbox_stale"
    SANDBOX_FINGERPRINT_MISMATCH = "sandbox_fingerprint_mismatch"
    ROLLBACK_UNAVAILABLE = "rollback_unavailable"
    COOLDOWN_ACTIVE = "cooldown_active"
    HOURLY_RATE_LIMIT_EXCEEDED = "hourly_rate_limit_exceeded"
    DAILY_RATE_LIMIT_EXCEEDED = "daily_rate_limit_exceeded"
    CONSECUTIVE_FAILURE_LIMIT_EXCEEDED = "consecutive_failure_limit_exceeded"
    EXECUTION_ALREADY_COMPLETED = "execution_already_completed"
    EXECUTION_IN_PROGRESS = "execution_in_progress"
    AUTHORIZATION_STALE = "authorization_stale"
    HARD_DENY = "hard_deny"
    AMBIGUOUS_POLICY_MATCH = "ambiguous_policy_match"
    NO_POLICY_MATCH = "no_policy_match"
    ISSUE_FINGERPRINT_MISSING = "issue_fingerprint_missing"
    DANGEROUS_ERROR_CLASSIFICATION = "dangerous_error_classification"
    SENSITIVE_ERROR_CLASSIFICATION = "sensitive_error_classification"
