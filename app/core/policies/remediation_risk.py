"""
Policy أو registry حتمي يقرر السماح أو الرفض أو التصنيف قبل التنفيذ.

الموقع في المعمارية: Core policy.
يُستدعى بواسطة: capabilities وMCP handlers.
يعتمد مباشرة على: app.core.contracts.remediation، app.core.policies.remediation_tools.
الحد المعماري: لا تنفذ SSH أو LLM أو persistence.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from app.core.contracts.remediation import RemediationAction, RemediationRisk
from app.core.policies.remediation_tools import NamedWriteToolRegistry


class RemediationRiskClassifier:
    """Deterministic risk rules; model output is never used for risk."""

    def __init__(self, registry: NamedWriteToolRegistry) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Core policy.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: registry.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._registry = registry

    def classify(self, action: RemediationAction, *, server_metadata: dict | None = None) -> RemediationRisk:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Core policy.

        تُستدعى عندما يصل workflow إلى classify؛ المدخلات المهمة: action، server_metadata.
        تعيد RemediationRisk أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        tool = self._registry.get(action.action_type)
        if tool is None:
            return RemediationRisk.CRITICAL
        tags = {str(item).lower() for item in (server_metadata or {}).get("tags", [])}
        if "production" in tags or "critical" in tags:
            if action.action_type in {"stop_service", "restart_service"}:
                return RemediationRisk.CRITICAL
        return RemediationRisk(tool.risk_level)

    def classify_actions(self, actions: list[RemediationAction], *, server_metadata: dict | None = None) -> RemediationRisk:
        """
        يقيّم أو يتحقق من شرط حتمي قبل السماح بالخطوة التالية ضمن طبقة Core policy.

        تُستدعى عندما يصل workflow إلى classify_actions؛ المدخلات المهمة: actions، server_metadata.
        تعيد RemediationRisk أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        levels = [self.classify(action, server_metadata=server_metadata) for action in actions]
        order = {risk: index for index, risk in enumerate(RemediationRisk)}
        return max(levels, key=lambda risk: order[risk]) if levels else RemediationRisk.CRITICAL
