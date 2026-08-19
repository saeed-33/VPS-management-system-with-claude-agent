"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class ServiceStateObservation:
    """
    يمثل الدليل المقروء عن حالة خدمة قبل أو بعد تنفيذ المعالجة.
    """
    state: str
    stdout: str = ""
    stderr: str = ""
    exit_status: int | None = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)
