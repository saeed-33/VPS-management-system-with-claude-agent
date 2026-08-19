"""Contract class extracted from investigation_read_models.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

@dataclass(slots=True, frozen=True)
class InvestigationSummaryReadModel:
    """
    ملخص حالة التحقيق المناسب للقوائم وشاشات المتابعة السريعة.

    يبين هل يلزم التحقيق ومن اختير له وما إذا كان runtime والتشخيص النهائي
    متاحين، دون تحميل الأدلة والتفاصيل التشغيلية كلها.
    """
    investigation_id: str
    server_id: int
    report_id: int
    analysis_id: int | None
    status: str
    should_investigate: bool
    detected_domains: tuple[str, ...]
    selected_specialists: tuple[str, ...]
    max_specialists: int
    max_rounds: int
    max_actions: int
    runtime_available: bool
    final_diagnosis_available: bool
    created_at: datetime
    updated_at: datetime
