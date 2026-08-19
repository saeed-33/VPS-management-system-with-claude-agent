"""Contract class extracted from specialist_reasoning.py during the structure refactor."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

class SpecialistRemediationActionOutput(BaseModel):
    """
    اقتراح فعل معالجة مسمى بعد اكتمال الدليل التشخيصي.

    الاقتراح لا ينفذ أي تغيير؛ يحوله منسق التحقيق لاحقًا إلى خطة مقترحة
    تخضع للمراجعة والـ sandbox والموافقة. حصر الأفعال هنا يمنع تحويل نص
    النموذج إلى أمر حر أو فعل غير معروف.
    """
    model_config = ConfigDict(extra="forbid")

    action_type: Literal[
        "start_service",
        "stop_service",
        "restart_service",
        "reload_service",
    ]
    target: str = Field(min_length=1, max_length=128)
    reason: str = Field(min_length=1, max_length=2000)
    expected_effect: str = Field(min_length=1, max_length=500)
    risk_level: Literal["low", "medium", "high", "critical"] = "medium"
    requires_approval: bool = True
    rollback_supported: bool = False
    verification_strategy: str = Field(default="", max_length=500)
    evidence_requirements: list[str] = Field(default_factory=list)
