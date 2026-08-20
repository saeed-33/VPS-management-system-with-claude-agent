"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

from .service_state_observation import ServiceStateObservation

class UnavailableEvidenceCollector:
    """
    يمثل جامع أدلة غير متاح ويعيد نتيجة عدم توفر الدليل.
    """
    def collect(self, **_kwargs) -> ServiceStateObservation:
        """
        يعيد دليلًا يوضح أن جمع حالة الخدمة غير متاح.
        """
        return ServiceStateObservation(
            state="unknown",
            error="safe_evidence_collector_not_configured",
        )
