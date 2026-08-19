"""
إدارة دورة معالجة المشكلة بعد التشخيص.

تنشئ الخدمة خطة قابلة للفحص، تتحقق منها في بيئة معزولة، تطلب الموافقة قبل
التغيير، تنفذ الخطة المعتمدة، وتتحقق من النتيجة أو تنفذ التراجع مع سجل تدقيق.
"""
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from sqlalchemy.exc import OperationalError

from app.capabilities.remediation.execution.service_state_evidence_collector import ServiceStateEvidenceCollector
from app.capabilities.remediation.execution.service_state_observation import ServiceStateObservation
from app.capabilities.remediation.execution.unavailable_evidence_collector import UnavailableEvidenceCollector
from app.capabilities.remediation.execution.unavailable_verification_runner import UnavailableVerificationRunner
from app.capabilities.remediation.execution.unavailable_write_runner import UnavailableWriteRunner
from app.capabilities.remediation.execution.verification_runner import VerificationRunner
from app.capabilities.remediation.execution.write_command_result import WriteCommandResult
from app.capabilities.remediation.execution.write_command_runner import WriteCommandRunner
from app.capabilities.remediation.sandbox_runtime import NativeSandboxRuntime
from app.core.contracts.sandbox_validation.sandbox_runtime_check import SandboxRuntimeCheck
from app.core.contracts.sandbox_validation.sandbox_target import SandboxTarget
from app.core.contracts.sandbox_validation.sandbox_validation_status import SandboxValidationStatus
from app.core.policies.sandbox_validation import validate_sandbox_target
from app.core.contracts.remediation.approval_status import ApprovalStatus
from app.core.contracts.remediation.create_remediation_plan_dto import CreateRemediationPlanDTO
from app.core.contracts.remediation.create_sandbox_result_dto import CreateSandboxResultDTO
from app.core.contracts.remediation.execution_status import ExecutionStatus
from app.core.contracts.remediation.remediation_action import RemediationAction
from app.core.contracts.remediation.remediation_plan_status import RemediationPlanStatus
from app.core.contracts.remediation.remediation_risk import RemediationRisk
from app.core.contracts.remediation.rollback_status import RollbackStatus
from app.core.contracts.remediation.verification_status import VerificationStatus
from app.core.contracts.autonomous_remediation.autonomous_authorization_status import AutonomousAuthorizationStatus
from app.core.contracts.autonomous_remediation.autonomous_authorization import AutonomousAuthorization
from app.core.contracts.analysis.error_classification import ErrorClassification
from app.core.policies.remediation_policy import RemediationPolicyEngine
from app.core.policies.remediation_risk import RemediationRiskClassifier
from app.core.policies.remediation_tools.named_write_tool_registry import NamedWriteToolRegistry
from app.core.policies.remediation_tools.factories import build_default_write_tool_registry
from app.core.utils.datetime import utc_now
from app.infrastructure.database.repositories.remediation_repository.repository import RemediationRepository


class _RemediationPlanningMixin:
    """ينظم مجموعة من عمليات خدمة المعالجة."""

    def propose_remediation(self, *, investigation_id: str, problem_summary: str,
                            diagnosis_claim_ids: list[str], evidence_ids: list[str]) -> dict:
        """
        ينشئ اقتراح معالجة من التشخيص والأدلة دون تنفيذ أي تغيير.
        """
        self._validate_links(diagnosis_claim_ids=diagnosis_claim_ids, evidence_ids=evidence_ids)
        if not investigation_id.strip():
            raise ValueError("investigation_id must not be empty.")
        if not problem_summary.strip():
            raise ValueError("problem_summary must not be empty.")
        return {
            "investigation_id": investigation_id,
            "problem_summary": problem_summary,
            "diagnosis_claim_ids": list(diagnosis_claim_ids),
            "evidence_ids": list(evidence_ids),
            "requires_plan": True,
            "production_application_allowed": False,
            "automatic_remediation_allowed": self._automatic_remediation_allowed,
        }

    def create_plan(self, *, investigation_id: str, title: str, problem_summary: str,
                    proposed_actions: list[dict], diagnosis_claim_ids: list[str], evidence_ids: list[str],
                    risk_level: str = RemediationRisk.MEDIUM.value, rollback_plan: str | None = None,
                    plan_id: str | None = None, server_id: int | None = None,
                    error_classification: str | None = None,
                    metadata: dict | None = None):
        """
        ينشئ خطة معالجة مرتبطة بالتشخيص والسيرفر والأفعال القابلة للتحقق.
        """
        self._validate_links(diagnosis_claim_ids=diagnosis_claim_ids, evidence_ids=evidence_ids)
        self._validate_actions(proposed_actions)
        action_models = [RemediationAction.from_dict(action) for action in proposed_actions]
        registered = [self._write_tools.get(action.action_type) is not None for action in action_models]
        deterministic_risk = self._risk_classifier.classify_actions(action_models)
        requested_risk = RemediationRisk(risk_level)
        effective_risk = deterministic_risk if all(registered) else requested_risk
        # لا يستطيع تقدير المستخدم خفض مستوى الخطر الذي قررته قواعد المعالجة.
        risk_order = {risk: index for index, risk in enumerate(RemediationRisk)}
        if risk_order[requested_risk] > risk_order[effective_risk]:
            effective_risk = requested_risk
        metadata = {
            "production_application_allowed": False,
            "automatic_remediation_allowed": self._automatic_remediation_allowed,
            "registered_actions": registered,
            **dict(metadata or {}),
        }
        if error_classification is not None:
            metadata["error_classification"] = ErrorClassification(
                error_classification
            ).value
        if self._issue_fingerprint_service is not None:
            trusted_issue_fingerprint = self._issue_fingerprint_service.derive(investigation_id)
            if trusted_issue_fingerprint:
                metadata["issue_fingerprint"] = trusted_issue_fingerprint

        return self._repository.create_plan(
            CreateRemediationPlanDTO(
                plan_id=plan_id or str(uuid4()),
                investigation_id=investigation_id,
                title=title,
                problem_summary=problem_summary,
                proposed_actions=list(proposed_actions),
                diagnosis_claim_ids=diagnosis_claim_ids,
                evidence_ids=evidence_ids,
                risk_level=effective_risk.value,
                rollback_plan=rollback_plan,
                metadata=metadata,
                server_id=server_id,
            )
        )

    def record_no_solution_found(self, *, investigation_id: str, title: str,
                                 problem_summary: str, diagnosis_claim_ids: list[str],
                                 evidence_ids: list[str], server_id: int | None = None,
                                 plan_id: str | None = None):
        """
        يسجل أن التحليل لم ينتج حلًا قابلًا للتنفيذ.
        """
        self._validate_links(diagnosis_claim_ids=diagnosis_claim_ids, evidence_ids=evidence_ids)
        return self._repository.create_no_solution_plan(
            plan_id=plan_id or str(uuid4()), investigation_id=investigation_id,
            title=title, problem_summary=problem_summary,
            diagnosis_claim_ids=diagnosis_claim_ids, evidence_ids=evidence_ids,
            server_id=server_id,
        )

    def test_in_sandbox(self, *, plan_id: str):
        """
        ينفذ اختبار الخطة في بيئة معزولة ويسجل النتيجة دون أثر على السيرفر الحقيقي.
        """
        plan = self._require_plan(plan_id)
        actions = plan.proposed_actions or []
        failed_reasons = [action.get("sandbox_failure_reason") for action in actions if isinstance(action, dict) and action.get("sandbox_failure_reason")]
        unsupported = [action.get("id", "unknown") for action in actions if isinstance(action, dict) and action.get("sandbox_supported", True) is False]
        for action_data in actions:
            action = RemediationAction.from_dict(action_data)
            if action.action_type != "legacy":
                try:
                    self._write_tools.resolve(action)
                except ValueError as exc:
                    failed_reasons.append(str(exc))
        passed = not failed_reasons and not unsupported
        result_id = str(uuid4())
        logs = ["Sandbox validation executed in isolated dry-run mode."]
        if unsupported:
            logs.append("Unsupported sandbox actions: " + ", ".join(str(item) for item in unsupported))
        logs.extend(str(item) for item in failed_reasons)
        result = self._repository.create_sandbox_result(
            CreateSandboxResultDTO(
                result_id=result_id,
                plan_id=plan.plan_id,
                status="passed" if passed else "failed",
                before_evidence_ids=list(plan.evidence_ids or []),
                after_evidence_ids=[f"sandbox:{result_id}"] if passed else [],
                logs=logs,
                metadata={"isolated": True, "write_capable": False},
            )
        )
        self._audit(plan, "sandbox_passed" if passed else "sandbox_failed", {"result_id": result_id})
        return result
