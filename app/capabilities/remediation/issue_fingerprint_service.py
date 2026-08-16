"""
حساب بصمة مستقرة للمشكلة المكتشفة.

تطبع الخدمة الحالة والمشكلة والإجراء المقترح ومعرفات الأدلة، ثم تنتج بصمة
تساعد على منع التكرار وربط الخطط المتشابهة.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata


class IssueFingerprintService:
    """
    يحوّل عناصر المشكلة التشغيلية إلى بصمة قابلة للمقارنة ومنع التكرار.
    """

    _SCHEMA = "issue-fingerprint-v1"

    def __init__(self, *, investigation_read_service) -> None:
        """
        يحفظ استراتيجية التطبيع أو الإصدار المستخدم لبصمة المشكلة.
        """
        self._investigation_read_service = investigation_read_service

    def derive(self, investigation_id: str) -> str | None:
        """
        يطبع المشكلة والأدلة والإجراء المقترح وينتج بصمة SHA ثابتة.
        """
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
        يوحد حالة النص والفراغات والقيم المتغيرة قبل إدخالها في البصمة.
        """
        text = unicodedata.normalize("NFKC", str(value or ""))
        return re.sub(r"\s+", " ", text.strip()).casefold()
