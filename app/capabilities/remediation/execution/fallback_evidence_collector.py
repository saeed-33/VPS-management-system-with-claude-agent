"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

from app.core.contracts.remediation.service_state_observation import ServiceStateObservation

class FallbackEvidenceCollector:
    """
    يمثل جامع أدلة احتياطياً يعيد نتيجة آمنة عند غياب المنفذ الحقيقي.
    """
    def collect(self, **_kwargs) -> ServiceStateObservation:
        """
        يعيد دليلًا يوضح أن جمع حالة الخدمة غير متاح.
        """
        return ServiceStateObservation(
            state="unknown",
            error="safe_evidence_collector_not_configured",
        )
