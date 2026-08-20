"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

from typing import Protocol

from .service_state_observation import ServiceStateObservation

class ServiceStateEvidenceCollector(Protocol):
    """
    يعرّف عقد جمع دليل حالة خدمة من السيرفر المستهدف.
    """
    def collect(self, *, server_id: int, service: str) -> ServiceStateObservation:
        """
        يعرّف عملية جمع دليل حالة الخدمة من المنفذ المرتبط بالسيرفر.
        """
        ...
