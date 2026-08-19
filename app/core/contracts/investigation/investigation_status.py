"""Contract class extracted from investigation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

class InvestigationStatus(StrEnum):
    """
    حالات التحقيق من إنشائه حتى اكتماله أو توقفه.
    """
    CREATED = "created"
    INVESTIGATING = "investigating"
    WAITING_FOR_EVIDENCE = "waiting_for_evidence"
    NO_EVIDENCE_FOUND = "no_evidence_found"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
