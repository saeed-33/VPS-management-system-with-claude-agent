"""
جزء من Remediation من التشخيص والاقتراح حتى sandbox/authorization والتنفيذ.

الموقع في المعمارية: Application capability / remediation.
يُستدعى بواسطة: Admin API أو MCP.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يسمح write operation بمجرد اقتراح LLM.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata


class IssueFingerprintService:
    """Derive a stable issue identity from persisted structured diagnosis claims."""

    _SCHEMA = "issue-fingerprint-v1"

    def __init__(self, *, investigation_read_service) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: investigation_read_service.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._investigation_read_service = investigation_read_service

    def derive(self, investigation_id: str) -> str | None:
        """Return a versioned SHA-256 identity, or None when diagnosis is unusable."""
        if not investigation_id or not investigation_id.strip():
            return None

        investigation = self._investigation_read_service.get(investigation_id)
        if investigation is None or not investigation.final_diagnosis_available:
            return None

        runtime = investigation.runtime
        if runtime is None or not isinstance(runtime.final_diagnosis, dict):
            return None

        claims = []
        for raw_claim in runtime.correlated_claims:
            if not isinstance(raw_claim, dict):
                continue
            title = self._normalize_text(raw_claim.get("title"))
            certainty = self._normalize_text(raw_claim.get("certainty"))
            metadata = raw_claim.get("metadata")
            states = ()
            if isinstance(metadata, dict):
                raw_states = metadata.get("diagnostic_states")
                if isinstance(raw_states, (list, tuple)):
                    states = tuple(sorted({self._normalize_text(item) for item in raw_states if self._normalize_text(item)}))
            if not title or not certainty:
                continue
            claims.append({
                "certainty": certainty,
                "diagnostic_states": list(states),
                "title": title,
            })

        if not claims:
            return None

        payload = {
            "schema": self._SCHEMA,
            "claims": sorted(claims, key=lambda item: json.dumps(item, sort_keys=True, ensure_ascii=False)),
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize_text(value) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى _normalize_text؛ المدخلات المهمة: value.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        text = unicodedata.normalize("NFKC", str(value or ""))
        return re.sub(r"\s+", " ", text.strip()).casefold()
