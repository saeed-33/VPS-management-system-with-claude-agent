"""
عقود نتائج تشغيل الاختصاصيين والتحقيق.

تحمل النماذج حالة التشغيل والمخرجات والنتائج المنظمة اللازمة لحفظ التقدم
وإعادة عرضه دون ربط طبقة التحقيق بنموذج تخزين محدد.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.core.contracts.investigation import (
    ServerInvestigationState,
    SpecialistResult,
    SpecialistTask,
)
from app.capabilities.investigation.specialist_investigation_loop import (
    SpecialistInvestigationLoopResult,
)


@dataclass(slots=True, frozen=True)
class InvestigationSpecialistRun:
    """
    يمثل سجل تشغيل اختصاصي داخل التحقيق.
    """
    specialist_slug: str
    task: SpecialistTask
    result: SpecialistResult
    loop_result: SpecialistInvestigationLoopResult | None


@dataclass(slots=True, frozen=True)
class InvestigationExecutionResult:
    """
    يمثل نتيجة تنفيذ تحقيق أو اختصاصي مع حالته وبياناته.
    """
    state: ServerInvestigationState
    runs: tuple[InvestigationSpecialistRun, ...]
    investigation_actions_used: int
