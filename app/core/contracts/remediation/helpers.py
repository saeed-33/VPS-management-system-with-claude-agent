"""عقود خطة المعالجة، الموافقة، التنفيذ، والتحقق من أثر التغيير."""

from __future__ import annotations

import hashlib

import json

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

from .remediation_risk import RemediationRisk

RiskLevel = RemediationRisk

def _canonical_json(value: Any) -> str:
    """
    يحول قيمة الخطة إلى JSON ثابت يصلح لبناء بصمة قابلة للمقارنة.

    يضمن ترتيب المفاتيح والشكل الموحد أن تعرف الخدمة هل تغيرت الخطة فعلًا قبل
    قبول موافقة أو تفويض قديم.
    """
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )

def remediation_fingerprint(
    *,
    plan_id: str,
    version: int,
    server_id: int | None,
    actions: list[dict[str, Any]],
    evidence_ids: list[str],
) -> str:
    """
    يبني بصمة ثابتة لخطة مرتبطة بإصدارها وسيرفرها وأدلتها وأفعالها.

    تستخدم البصمة لمنع تطبيق موافقة أو نتيجة sandbox على خطة تغيرت منذ إصدارها.
    """
    payload = {
        "plan_id": plan_id,
        "version": version,
        "server_id": server_id,
        "actions": actions,
        "evidence_ids": sorted(str(item) for item in evidence_ids),
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
