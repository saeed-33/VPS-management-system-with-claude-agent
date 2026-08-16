"""
جزء من واجهة الإدارة يعرّف route أو payload أو عرضًا للمشغل.

الموقع في المعمارية: Administration interface.
يُستدعى بواسطة: FastAPI أو متصفح الإدارة.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: العرض والتحقق الشكلي لا يمنحان صلاحية تنفيذ؛ authorization في الخدمة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AutonomousPolicyRequest(BaseModel):
    """
    يمثل AutonomousPolicyRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    policy_id: str | None = Field(default=None, min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=4000)
    issue_fingerprint: str = Field(min_length=1, max_length=128)
    allowed_action_type: str = Field(default="start_service", min_length=1, max_length=80)
    allowed_target_pattern: str = Field(min_length=1, max_length=128)
    maximum_risk: str = Field(default="low", min_length=1, max_length=20)
    required_evidence: list[str] = Field(default_factory=lambda: [
        "diagnosis", "plan", "sandbox_before", "sandbox_after", "verification"
    ])
    minimum_confidence: float = Field(default=0.0, ge=0, le=1)
    minimum_success_count: int = Field(default=0, ge=0)
    maximum_failure_rate: float = Field(default=0.0, ge=0, le=1)
    maximum_rollback_failure_rate: float = Field(default=0.0, ge=0, le=1)
    allowed_server_ids: list[int] = Field(default_factory=list, min_length=0)
    allowed_server_tags: list[str] = Field(default_factory=list, min_length=0)
    sandbox_required: bool = True
    sandbox_max_age_seconds: int = Field(default=3600, ge=1)
    rollback_required: bool = True
    cooldown_seconds: int = Field(default=0, ge=0)
    max_executions_per_hour: int = Field(default=1, ge=1)
    max_executions_per_day: int = Field(default=3, ge=1)
    max_consecutive_failures: int = Field(default=1, ge=1)
    auto_suspend_on_failure: bool = True
    created_by: str = Field(default="admin", min_length=1, max_length=120)


class AutonomousPolicyUpdateRequest(BaseModel):
    """
    يمثل AutonomousPolicyUpdateRequest مسؤولية محددة داخل طبقة Administration interface.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه FastAPI أو متصفح الإدارة
    ويعتمد على BaseModel وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    allowed_target_pattern: str | None = Field(default=None, min_length=1, max_length=128)
    minimum_confidence: float | None = Field(default=None, ge=0, le=1)
    minimum_success_count: int | None = Field(default=None, ge=0)
    maximum_failure_rate: float | None = Field(default=None, ge=0, le=1)
    maximum_rollback_failure_rate: float | None = Field(default=None, ge=0, le=1)
    updated_by: str = Field(default="admin", min_length=1, max_length=120)
