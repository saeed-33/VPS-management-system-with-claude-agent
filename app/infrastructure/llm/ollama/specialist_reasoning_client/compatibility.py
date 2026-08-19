"""تطبيع أسماء حقول مخرجات Ollama."""
from __future__ import annotations

import json
from typing import Any

def normalize_compatibility_aliases(content: str) -> str:
    """
    يطبّع أخطاء أسماء الحقول الشائعة قبل التحقق الصارم من العقد.

    لا يضيف هذا المسار إجراءً جديداً ولا يتجاوز التحقق؛ إنه يحول فقط
    aliases معروفة من بعض نماذج Ollama ثم يترك Pydantic يتحقق من البنية
    والقيم والمراجع كما هي.
    """
    try:
        payload: Any = json.loads(content)
    except json.JSONDecodeError:
        # دع Pydantic/مسار إعادة المحاولة يتعامل مع JSON المقطوع.
        return content
    if not isinstance(payload, dict):
        return content

    hypotheses = payload.get("hypotheses")
    if isinstance(hypotheses, list):
        for item in hypotheses:
            if isinstance(item, dict):
                item.pop("knowledge_source_ids", None)

    actions = payload.get("recommended_remediation_actions")
    if isinstance(actions, list):
        allowed = {
            "action_type",
            "target",
            "reason",
            "expected_effect",
            "risk_level",
            "requires_approval",
            "rollback_supported",
            "verification_strategy",
            "evidence_requirements",
        }
        for item in actions:
            if not isinstance(item, dict):
                continue
            if "action_type" not in item and item.get("action"):
                item["action_type"] = item.pop("action")
            if "target" not in item and item.get("service"):
                item["target"] = item.pop("service")
            if not item.get("reason"):
                item["reason"] = (
                    item.get("description")
                    or item.get("rationale")
                    or "Named remediation action supported by the supplied evidence."
                )
            if not item.get("expected_effect"):
                item["expected_effect"] = (
                    item.get("expected_state")
                    or "The named service reaches the expected state."
                )
            for key in tuple(item):
                if key not in allowed:
                    item.pop(key, None)

    return json.dumps(payload, ensure_ascii=False)
