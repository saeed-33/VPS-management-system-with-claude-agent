"""Contract class extracted from remediation.py during the structure refactor."""

from __future__ import annotations

import hashlib

import json

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

@dataclass(slots=True, frozen=True)
class CreateSandboxResultDTO:
    """
    نتيجة اختبار خطة في البيئة المعزولة مع أدلة الحالة قبل وبعد الاختبار.
    """
    result_id: str
    plan_id: str
    status: str
    before_evidence_ids: list[str]
    after_evidence_ids: list[str]
    logs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """يتحقق من هوية نتيجة الاختبار والخطة ومن أن حالتها passed أو failed."""
        if not self.result_id.strip():
            raise ValueError("result_id must not be empty.")
        if not self.plan_id.strip():
            raise ValueError("plan_id must not be empty.")
        if self.status not in {"passed", "failed"}:
            raise ValueError("sandbox status is invalid.")
