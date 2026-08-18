"""
إنشاء خطط معالجة مقترحة من التشخيص النهائي.

تجمع هذه الخدمة الاقتراحات المنظمة التي خرجت من المتخصصين، وتحوّلها إلى
خطط بحالة ``proposed`` فقط. لا تختبر الخطة ولا تطلب موافقة ولا تنفذ أي
تغيير على السيرفر.
"""
from __future__ import annotations

import logging
from uuid import uuid4

from app.core.contracts.remediation import RemediationAction
from app.core.policies.remediation_tools import NamedWriteToolRegistry, build_default_write_tool_registry


logger = logging.getLogger(__name__)


class RemediationPlanProposalService:
    """
    ينسق إنشاء اقتراح واحد أو أكثر مع منع التكرار والتحقق من الأفعال المسماة.
    """

    def __init__(
        self,
        *,
        repository,
        remediation_service,
        write_tool_registry: NamedWriteToolRegistry | None = None,
    ) -> None:
        """
        يربط مستودع الخطط بخدمة المعالجة التي تفرض عقود الخطة ومخاطرها.
        """
        self._repository = repository
        self._remediation_service = remediation_service
        self._write_tools = write_tool_registry or build_default_write_tool_registry()

    def create_from_diagnosis(self, *, diagnosis, server_id: int | None = None):
        """
        ينشئ خططًا مقترحة من التشخيص المكتمل دون أي أثر تنفيذي.

        إذا لم يخرج المتخصصون فعلاً مسمى قابلًا للتنفيذ، يسجل النظام حالة
        ``no_solution_found`` حتى يظهر سبب عدم وجود خطة بدلاً من اختلاق إجراء.
        """
        investigation_id = str(getattr(diagnosis, "investigation_id", "")).strip()
        if not investigation_id:
            raise ValueError("A completed diagnosis requires an investigation_id.")

        existing = self._repository.get_latest_plan_for_investigation(investigation_id)
        if existing is not None:
            return [existing]

        claims = tuple(getattr(diagnosis, "claims", ()) or ())
        evidence_ids = list(dict.fromkeys(str(item) for item in (getattr(diagnosis, "evidence_ids", ()) or ()) if str(item).strip()))
        claim_ids = [str(item.claim_id) for item in claims if str(getattr(item, "claim_id", "")).strip()]
        if not claim_ids or not evidence_ids:
            logger.warning(
                "Remediation plan proposal skipped without diagnosis links | "
                "investigation_id=%s | claims=%s | evidence=%s",
                investigation_id,
                len(claim_ids),
                len(evidence_ids),
            )
            return []

        metadata = dict(getattr(diagnosis, "metadata", {}) or {})
        raw_actions = metadata.get("recommended_remediation_actions", [])
        actions = self._supported_actions(raw_actions)
        summary = str(getattr(diagnosis, "summary", "")).strip()

        if not actions:
            logger.info(
                "No executable remediation action found | investigation_id=%s",
                investigation_id,
            )
            return [
                self._remediation_service.record_no_solution_found(
                    investigation_id=investigation_id,
                    title="لا يوجد إجراء معالجة آمن مقترح",
                    problem_summary=summary or "اكتمل التشخيص دون إجراء مسمى قابل للمراجعة.",
                    diagnosis_claim_ids=claim_ids,
                    evidence_ids=evidence_ids,
                    server_id=server_id,
                )
            ]

        plans = []
        for action in actions:
            target = action["target"]
            action_type = action["action_type"]
            reason = action.get("reason") or summary
            rollback_plan = (
                "يُعاد الإجراء العكسي المسجل بعد التحقق من الحالة السابقة."
                if action.get("rollback_supported")
                else None
            )
            plans.append(
                self._remediation_service.create_plan(
                    investigation_id=investigation_id,
                    title=f"اقتراح معالجة: {action_type} على {target}",
                    problem_summary=summary or reason,
                    proposed_actions=[action],
                    diagnosis_claim_ids=claim_ids,
                    evidence_ids=evidence_ids,
                    risk_level=action.get("risk_level", "medium"),
                    rollback_plan=rollback_plan,
                    plan_id=f"inv-plan-{uuid4().hex}",
                    server_id=server_id,
                    metadata={
                        "source": "completed_investigation",
                        "proposal_status": "awaiting_operator_approval",
                        "diagnosis_summary": summary,
                    },
                )
            )
        return plans

    def _supported_actions(self, raw_actions) -> list[dict]:
        """
        يختار الأفعال المسماة التي يملك النظام أداة لها ويتحقق من هدف الخدمة.
        """
        if not isinstance(raw_actions, (list, tuple)):
            return []

        supported: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for raw in raw_actions:
            if not isinstance(raw, dict):
                continue
            try:
                action = RemediationAction.from_dict(raw)
                tool = self._write_tools.resolve(action)
            except (TypeError, ValueError):
                continue
            key = (action.action_type, action.target)
            if key in seen:
                continue
            seen.add(key)
            supported.append({
                **action.to_dict(),
                "expected_effect": action.expected_effect or tool.expected_effect,
                "rollback_supported": bool(action.rollback_supported and tool.rollback_action),
            })
        return supported
