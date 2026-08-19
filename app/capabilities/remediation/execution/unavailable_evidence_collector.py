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



_WINDOWS_ABSOLUTE_PATH = re.compile(
    r"^(?P<drive>[A-Za-z]):[\\/](?P<rest>.+)$"
)


def _resolve_runtime_file_path(value: str) -> str:
    """
    يحل مسار ملف runtime المسموح باستخدامه في تنفيذ المعالجة.
    """
    raw = str(value).strip()

    direct = Path(raw)
    if direct.is_file():
        return str(direct)

    if os.getenv("WSL_DISTRO_NAME", "").strip():
        match = _WINDOWS_ABSOLUTE_PATH.match(raw)

        if match:
            drive = match.group("drive").lower()
            rest = match.group("rest").replace("\\", "/")

            translated = Path("/mnt") / drive / rest

            if translated.is_file():
                return str(translated)

    return raw
