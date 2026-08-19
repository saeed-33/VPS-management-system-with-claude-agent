"""Tests for test real autonomous remediation.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest


RUN_REAL_ACCEPTANCE = os.getenv("REAL_PHASE7_ACCEPTANCE_ENABLED", "").strip() == "1"

pytestmark = pytest.mark.skipif(
    not RUN_REAL_ACCEPTANCE,
    reason=(
        "Real Phase 7 acceptance is opt-in; set "
        "REAL_PHASE7_ACCEPTANCE_ENABLED=1."
    ),
)


SERVER_ID = 4
SERVER_NAME = "phase5-lab"
SERVICE_NAME = "ai-vps-remediation-test.service"
ACTION_TYPE = "start_service"
ACCEPTANCE_ACTOR = "phase7-real-acceptance"


def _load_operational_runtime_env(env_path: Path | None = None) -> None:
    """Load operational settings, preserving explicit process environment values."""
    from dotenv import dotenv_values

    resolved_env_path = env_path or Path(__file__).resolve().parents[3] / ".env"
    values = dotenv_values(resolved_env_path)
    required = (
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "SSH_KNOWN_HOSTS_PATH",
    )
    for key in (*required, "DEFAULT_SSH_PRIVATE_KEY_PATH"):
        current = str(os.environ.get(key) or "").strip()
        if current:
            continue

        fallback = str(values.get(key) or "").strip()
        if fallback:
            os.environ[key] = fallback

    missing = [key for key in required if not str(os.environ.get(key) or "").strip()]
    if missing:
        pytest.fail(
            "PHASE7_REAL_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: missing "
            + ", ".join(missing)
        )


def _require_acceptance_environment() -> None:
    """Reject every unsafe or ambiguous real-runtime configuration."""
    if os.getenv("AUTOMATIC_REMEDIATION_ALLOWED", "").strip().lower() != "true":
        pytest.fail(
            "PHASE7_REAL_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: "
            "AUTOMATIC_REMEDIATION_ALLOWED=true is required for this run."
        )
    if os.getenv("SAFE_REMEDIATION_SERVER_ID", "").strip() != str(SERVER_ID):
        pytest.fail(
            "PHASE7_REAL_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: "
            "SAFE_REMEDIATION_SERVER_ID must be 4."
        )
    if os.getenv("SAFE_REMEDIATION_SERVER_NAME", "").strip() != SERVER_NAME:
        pytest.fail(
            "PHASE7_REAL_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: "
            "SAFE_REMEDIATION_SERVER_NAME must be phase5-lab."
        )
    if os.getenv("SAFE_REMEDIATION_SERVICE", "").strip() != SERVICE_NAME:
        pytest.fail(
            "PHASE7_REAL_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: "
            "SAFE_REMEDIATION_SERVICE must be ai-vps-remediation-test.service."
        )
    if not os.getenv("WSL_DISTRO_NAME", "").strip():
        pytest.fail(
            "PHASE7_REAL_ACCEPTANCE = BLOCKED_BY_SANDBOX_RUNTIME: "
            "WSL2 runtime was not detected."
        )
    if not os.getenv("PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE", "").strip():
        pytest.fail(
            "PHASE7_REAL_ACCEPTANCE = BLOCKED_BY_SANDBOX_RUNTIME: "
            "PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE is required."
        )


def _assert_safe_target(container):
    """Prove the database target identity and non-production designation."""
    from app.core.contracts.sandbox_validation.sandbox_target import SandboxTarget
    from app.core.policies.sandbox_validation import validate_sandbox_target

    server = container.server_repository.get_by_id(SERVER_ID)
    if server is None:
        pytest.fail(
            "PHASE7_REAL_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: "
            "server 4 was not found."
        )
    target = SandboxTarget(
        server_id=SERVER_ID,
        server_name=SERVER_NAME,
        service=SERVICE_NAME,
        designation=server.description or "",
    )
    try:
        validate_sandbox_target(server=server, target=target)
    except ValueError as exc:
        pytest.fail(
            "PHASE7_REAL_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: "
            f"{exc}"
        )
    return server


def _assert_native_sandbox_available():
    """Run the real attestation check before any remediation write."""
    from app.capabilities.remediation.sandbox_runtime import NativeSandboxRuntime

    result = NativeSandboxRuntime().check()
    if not result.available:
        pytest.fail(
            "PHASE7_REAL_ACCEPTANCE = BLOCKED_BY_SANDBOX_RUNTIME: "
            f"{result.reason}"
        )
    return result


def _persist_acceptance_investigation(container) -> tuple[str, str, str, str]:
    """Persist a real structured diagnosis through project services."""
    from app.capabilities.investigation.correlation.correlated_diagnosis_claim import CorrelatedDiagnosisClaim
    from app.capabilities.investigation.correlation.diagnosis_certainty import DiagnosisCertainty
    from app.capabilities.investigation.correlation.final_diagnosis import FinalDiagnosis
    from app.capabilities.investigation.execution_contracts.investigation_execution_result import InvestigationExecutionResult
    from app.core.contracts.final_diagnosis.final_diagnosis_narrative import FinalDiagnosisNarrative
    from app.capabilities.investigation.investigation_router.investigation_routing_decision import InvestigationRoutingDecision
    from app.capabilities.investigation.investigation_router.routing_reason import RoutingReason
    from app.core.contracts.analysis.analysis_health_status import AnalysisHealthStatus
    from app.core.contracts.analysis.analysis_issue import AnalysisIssue
    from app.core.contracts.analysis.report_analysis_result import ReportAnalysisResult
    from app.core.contracts.investigation.evidence_kind import EvidenceKind
    from app.core.contracts.investigation.evidence_reference import EvidenceReference
    from app.core.contracts.investigation.investigation_budget import InvestigationBudget
    from app.core.contracts.investigation.investigation_status import InvestigationStatus
    from app.core.contracts.investigation.server_investigation_state import ServerInvestigationState
    from app.core.contracts.reports.monitoring_report_data import MonitoringReportData
    from app.core.contracts.reports.monitoring_report_status import MonitoringReportStatus
    from app.core.utils.datetime import utc_now

    now = utc_now()
    report_id = container.report_repository.create(
        MonitoringReportData(
            server_id=SERVER_ID,
            status=MonitoringReportStatus.SUCCESS,
            started_at=now,
            finished_at=now,
            duration_ms=0.0,
            connection_successful=True,
            error_message=None,
            commands_total=0,
            commands_succeeded=0,
            commands_failed=0,
        )
    )
    analysis = container.analysis_repository.create_pending(
        report_id=report_id,
        server_id=SERVER_ID,
        provider_name="phase7-real-acceptance",
        model_name="persisted-fixture",
    )
    container.analysis_repository.mark_completed(
        analysis_id=analysis.id,
        result=ReportAnalysisResult(
            health_status=AnalysisHealthStatus.WARNING,
            summary="The dedicated lab service is intentionally inactive.",
            issues=[
                AnalysisIssue(
                    severity="warning",
                    title="Dedicated remediation service inactive",
                    description="The safe acceptance service is inactive and can be started.",
                    evidence="systemd service state is inactive",
                )
            ],
        ),
        finished_at=now,
        duration_ms=0.0,
    )

    routing = InvestigationRoutingDecision(
        should_investigate=True,
        reasons=(RoutingReason.ANALYSIS_ISSUES,),
        detected_domains=("service-management",),
        candidate_specialists=(),
        selected_specialists=(),
        unmatched_issue_indexes=(),
        registry_size=0,
        candidate_limit=12,
        selection_limit=4,
    )
    investigation = container.investigation_persistence_service.persist_routing_decision(
        server_id=SERVER_ID,
        report_id=report_id,
        analysis_id=analysis.id,
        decision=routing,
        budget=InvestigationBudget(max_specialists=1, max_rounds=1, max_actions=1),
        routing_version="phase7-real-acceptance-v1",
    )
    investigation_id = investigation.investigation_id

    evidence_id = f"phase7-diagnosis-evidence-{uuid4().hex}"
    evidence = EvidenceReference(
        evidence_id=evidence_id,
        kind=EvidenceKind.DERIVED_FINDING,
        title="Dedicated service inactive diagnosis evidence",
        source_id=report_id,
        excerpt="The dedicated non-production service is intentionally inactive.",
        metadata={
            "investigation_id": investigation_id,
            "server_id": SERVER_ID,
            "service": SERVICE_NAME,
        },
    )
    state = ServerInvestigationState(
        investigation_id=investigation_id,
        server_id=SERVER_ID,
        report_id=report_id,
        analysis_id=analysis.id,
        status=InvestigationStatus.COMPLETED,
        budget=InvestigationBudget(max_specialists=1, max_rounds=1, max_actions=1),
        evidence=[evidence],
        metadata={"orchestrator": "phase7-real-acceptance-fixture"},
    )
    container.investigation_runtime_snapshot_service.persist(
        investigation_id=investigation_id,
        execution_result=InvestigationExecutionResult(
            state=state,
            runs=(),
            investigation_actions_used=0,
        ),
    )

    claim = CorrelatedDiagnosisClaim(
        claim_id=f"phase7-diagnosis-claim-{uuid4().hex}",
        title="Dedicated service inactive",
        description="The dedicated non-production service is intentionally inactive.",
        certainty=DiagnosisCertainty.CONFIRMED,
        confidence=1.0,
        specialist_slugs=("phase7-real-acceptance-fixture",),
        evidence_ids=(evidence_id,),
        metadata={"diagnostic_states": ["service_inactive"]},
    )
    diagnosis = FinalDiagnosis(
        investigation_id=investigation_id,
        summary="The dedicated service is inactive and safe to start for acceptance.",
        claims=(claim,),
        conflicts=(),
        confirmed_count=1,
        probable_count=0,
        unknown_count=0,
        conflict_count=0,
        evidence_ids=(evidence_id,),
        specialist_slugs=("phase7-real-acceptance-fixture",),
        metadata={"source": "persisted-real-acceptance-fixture"},
    )
    narrative = FinalDiagnosisNarrative(
        summary=diagnosis.summary,
        claim_ids=(claim.claim_id,),
        conflict_ids=(),
        operator_notes=("Dedicated non-production acceptance fixture.",),
        provider_name="phase7-real-acceptance",
        model_name="persisted-fixture",
        used_fallback=False,
        metadata={"fixture": True},
    )
    container.investigation_repository.persist_finalization(
        investigation_id=investigation_id,
        merge=lambda model, metadata: container.investigation_runtime_snapshot_service.merge_finalization(
            metadata=metadata,
            final_diagnosis=diagnosis,
            narrative=narrative,
        ),
    )

    detail = container.investigation_read_service.get(investigation_id)
    issue_fingerprint = container.issue_fingerprint_service.derive(investigation_id)
    if detail is None or not detail.final_diagnosis_available or not issue_fingerprint:
        pytest.fail(
            "PHASE7_REAL_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: "
            "persisted structured diagnosis did not produce a trusted issue fingerprint."
        )
    return investigation_id, claim.claim_id, evidence_id, issue_fingerprint


def _create_plan(container, *, investigation_id: str, claim_id: str, evidence_id: str, label: str):
    """Create a single low-risk named action without caller fingerprint input."""
    return container.remediation_service.create_plan(
        plan_id=f"phase7-real-{label}-{uuid4().hex}",
        investigation_id=investigation_id,
        title="Phase 7 dedicated service acceptance",
        problem_summary="The dedicated non-production service is intentionally inactive.",
        proposed_actions=[
            {
                "id": f"phase7-start-{label}-{uuid4().hex}",
                "action_type": ACTION_TYPE,
                "target": SERVICE_NAME,
                "reason": "Start only the dedicated non-production acceptance service.",
            }
        ],
        diagnosis_claim_ids=[claim_id],
        evidence_ids=[evidence_id],
        risk_level="low",
        server_id=SERVER_ID,
    )


def _assert_inactive(container, plan_id: str) -> None:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى _assert_inactive؛ المدخلات المهمة: container، plan_id.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    observation = container.remediation_service.collect_service_evidence(
        plan_id=plan_id,
        server_id=SERVER_ID,
        service=SERVICE_NAME,
        phase="acceptance_state_check",
    )
    assert observation.observed_state == "inactive", (
        "The dedicated acceptance service must be inactive before/after "
        "each controlled iteration."
    )


def _validate_native_sandbox(container, plan):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى _validate_native_sandbox؛ المدخلات المهمة: container، plan.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    validation = container.remediation_service.validate_in_isolated_sandbox(
        plan_id=plan.plan_id,
        target_server_id=SERVER_ID,
        target_server_name=SERVER_NAME,
        target_service=SERVICE_NAME,
    )
    assert validation.status == "passed"
    assert validation.verification_status == "verified"
    assert validation.server_id == SERVER_ID
    assert validation.service == SERVICE_NAME
    assert validation.action_type == ACTION_TYPE
    assert validation.plan_id == plan.plan_id
    assert validation.plan_fingerprint == plan.plan_fingerprint
    assert validation.before_evidence_ids
    assert validation.after_evidence_ids
    assert validation.validation_metadata.get("restored_state") == "inactive"
    assert container.remediation_repository.sandbox_evidence_belongs(
        validation=validation
    )
    return validation


def _assert_supervised_execution(container, plan, approval, label: str):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى _assert_supervised_execution؛ المدخلات المهمة: container، plan، approval، label.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    outcome = container.remediation_service.apply_approved(
        plan_id=plan.plan_id,
        approval_id=approval.approval_id,
        server_id=SERVER_ID,
        actor=ACCEPTANCE_ACTOR,
        idempotency_key=f"phase7-real-supervised-{label}-{plan.plan_id}",
    )
    assert outcome["applied"] is True
    execution = container.remediation_service.get_latest_execution(plan.plan_id)
    assert execution is not None
    assert execution.status == "succeeded"
    assert execution.before_evidence_ids
    assert execution.after_evidence_ids
    assert execution.execution_metadata.get("autonomous") is False
    plan_after = container.remediation_service.get_plan(plan.plan_id)
    assert plan_after.execution_status == "succeeded"
    assert plan_after.verification_status == "verified"
    active = container.remediation_repository.get_evidence(execution.after_evidence_ids[0])
    assert active is not None
    assert active.plan_id == plan.plan_id
    assert active.execution_id == execution.execution_id
    assert active.server_id == SERVER_ID
    assert active.service == SERVICE_NAME
    assert active.observed_state == "active"

    rollback = container.remediation_service.rollback(
        plan_id=plan.plan_id,
        execution_id=execution.execution_id,
        server_id=SERVER_ID,
        actor=ACCEPTANCE_ACTOR,
    )
    assert rollback["rolled_back"] is True
    final = container.remediation_repository.get_evidence(rollback["after_evidence_ids"][0])
    assert final is not None
    assert final.plan_id == plan.plan_id
    assert final.execution_id == execution.execution_id
    assert final.observed_state == "inactive"
    _assert_inactive(container, plan.plan_id)
    return execution, rollback


def _assert_history_delta(baseline, current) -> None:
    """Require exactly three new clean supervised executions over the baseline."""
    assert current.supervised_execution_count == baseline.supervised_execution_count + 3
    assert current.successful_execution_count == baseline.successful_execution_count + 3
    assert current.verified_success_count == baseline.verified_success_count + 3
    assert current.failed_execution_count == baseline.failed_execution_count
    assert current.verification_failure_count == baseline.verification_failure_count
    assert current.rollback_failure_count == baseline.rollback_failure_count


def _assert_candidate_delta(baseline, current) -> None:
    """Require candidate counts to include three new successes without new failures."""
    baseline_execution_count = baseline.execution_count if baseline else 0
    baseline_verified_success_count = baseline.verified_success_count if baseline else 0
    baseline_failure_count = baseline.failure_count if baseline else 0
    baseline_rollback_failure_count = baseline.rollback_failure_count if baseline else 0
    assert current.execution_count == baseline_execution_count + 3
    assert current.verified_success_count == baseline_verified_success_count + 3
    assert current.failure_count == baseline_failure_count
    assert current.rollback_failure_count == baseline_rollback_failure_count
    assert current.success_rate == (
        (current.execution_count - current.failure_count) / current.execution_count
    )


def _restore_active_plans(container, plan_ids: list[str]) -> list[str]:
    """Use only the bounded project rollback path during failure cleanup."""
    errors = []
    for plan_id in plan_ids:
        try:
            plan = container.remediation_service.get_plan(plan_id)
            if plan is None or plan.server_id != SERVER_ID:
                continue
            observation = container.remediation_service.collect_service_evidence(
                plan_id=plan_id,
                server_id=SERVER_ID,
                service=SERVICE_NAME,
                phase="acceptance_cleanup_state_check",
            )
            if observation.observed_state != "active":
                continue
            execution = container.remediation_service.get_latest_execution(plan_id)
            if execution is None:
                errors.append(f"{plan_id}: active state has no controlled execution to rollback")
                continue
            result = container.remediation_service.rollback(
                plan_id=plan_id,
                execution_id=execution.execution_id,
                server_id=SERVER_ID,
                actor=f"{ACCEPTANCE_ACTOR}-cleanup",
            )
            if not result.get("rolled_back"):
                errors.append(f"{plan_id}: controlled rollback returned false")
        except Exception as exc:  # pragma: no cover - real cleanup diagnostics
            errors.append(f"{plan_id}: {type(exc).__name__}: {exc}")
    return errors


def test_phase7_real_autonomous_remediation_acceptance():
    """Run the complete opt-in Phase 7 happy path against the dedicated lab."""
    _load_operational_runtime_env()
    _require_acceptance_environment()

    from app.composition import container
    from app.core.config import settings

    if settings.automatic_remediation_allowed is not True:
        pytest.fail(
            "PHASE7_REAL_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: "
            "production composition did not receive explicit automatic enablement."
        )
    _assert_safe_target(container)
    _assert_native_sandbox_available()

    plan_ids: list[str] = []
    policy_id: str | None = None
    original_error = None
    result = None
    try:
        investigation_id, claim_id, evidence_id, issue_fingerprint = _persist_acceptance_investigation(container)
        baseline_history = container.autonomous_execution_service.history(
            issue_fingerprint=issue_fingerprint,
            action_type=ACTION_TYPE,
            target=SERVICE_NAME,
        )
        baseline_candidate = next(
            (
                item
                for item in container.autonomous_candidate_service.list_candidates()
                if item.issue_fingerprint == issue_fingerprint
                and item.action_type == ACTION_TYPE
                and item.target == SERVICE_NAME
            ),
            None,
        )

        supervised_plans = []
        for index in range(1, 4):
            plan = _create_plan(
                container,
                investigation_id=investigation_id,
                claim_id=claim_id,
                evidence_id=evidence_id,
                label=f"supervised-{index}",
            )
            plan_ids.append(plan.plan_id)
            supervised_plans.append(plan)
            assert plan.plan_metadata.get("issue_fingerprint") == issue_fingerprint
            if index == 1:
                _assert_inactive(container, plan.plan_id)
            else:
                _assert_inactive(container, supervised_plans[-2].plan_id)
            validation = _validate_native_sandbox(container, plan)
            assert validation.validation_metadata.get("restored_state") == "inactive"
            approval_request = container.remediation_service.request_approval(plan_id=plan.plan_id)
            approval = container.remediation_service.approve(
                approval_id=approval_request.approval_id,
                approver=ACCEPTANCE_ACTOR,
            )
            _assert_supervised_execution(container, plan, approval, f"{index}")

        assert len({plan.plan_metadata["issue_fingerprint"] for plan in supervised_plans}) == 1
        assert len({plan.plan_fingerprint for plan in supervised_plans}) == 3

        history = container.autonomous_execution_service.history(
            issue_fingerprint=issue_fingerprint,
            action_type=ACTION_TYPE,
            target=SERVICE_NAME,
        )
        _assert_history_delta(baseline_history, history)

        candidates = container.autonomous_candidate_service.list_candidates()
        candidate = next(
            (
                item
                for item in candidates
                if item.issue_fingerprint == issue_fingerprint
                and item.action_type == ACTION_TYPE
                and item.target == SERVICE_NAME
            ),
            None,
        )
        assert candidate is not None
        _assert_candidate_delta(baseline_candidate, candidate)
        assert "eligible_for_policy_review" in candidate.reason_codes

        policy = container.autonomous_policy_service.create(
            policy_id=f"phase7-real-policy-{uuid4().hex}",
            name="Phase 7 real acceptance policy",
            description="Dedicated non-production acceptance policy.",
            status="enabled",
            issue_fingerprint=issue_fingerprint,
            allowed_action_type=ACTION_TYPE,
            allowed_target_pattern=SERVICE_NAME,
            maximum_risk="low",
            minimum_success_count=3,
            maximum_failure_rate=0.0,
            maximum_rollback_failure_rate=0.0,
            allowed_server_ids=[SERVER_ID],
            sandbox_required=True,
            rollback_required=True,
            cooldown_seconds=0,
            max_executions_per_hour=2,
            max_executions_per_day=2,
            max_consecutive_failures=1,
            auto_suspend_on_failure=True,
            created_by=ACCEPTANCE_ACTOR,
            updated_by=ACCEPTANCE_ACTOR,
        )
        policy_id = policy.policy_id
        assert policy.status == "enabled"
        assert policy.version == 1

        autonomous_plan = _create_plan(
            container,
            investigation_id=investigation_id,
            claim_id=claim_id,
            evidence_id=evidence_id,
            label="autonomous",
        )
        plan_ids.append(autonomous_plan.plan_id)
        assert autonomous_plan.plan_metadata.get("issue_fingerprint") == issue_fingerprint
        assert autonomous_plan.plan_fingerprint not in {item.plan_fingerprint for item in supervised_plans}
        _assert_inactive(container, autonomous_plan.plan_id)
        sandbox = _validate_native_sandbox(container, autonomous_plan)
        assert sandbox.plan_fingerprint == autonomous_plan.plan_fingerprint

        # The evaluator intentionally requires the Phase 6 lifecycle to mark
        # this plan ready. Do not mutate the plan here; a missing transition is
        # a production wiring defect, not something an acceptance test may bypass.
        refreshed_plan = container.remediation_service.get_plan(autonomous_plan.plan_id)
        assert refreshed_plan.status in {"sandbox_passed", "approved"}, (
            "Phase 6 passed validation but did not transition the plan to a "
            "Phase 7-ready state."
        )

        decision, decided_plan, action, matched_policy, decided_sandbox, _ = container.autonomous_execution_service.evaluate(
            plan_id=autonomous_plan.plan_id
        )
        assert decision.outcome.value == "auto_execute"
        assert "policy_match" in decision.reason_codes
        assert decision.policy_id == policy.policy_id
        assert decision.policy_version == policy.version
        assert decision.issue_fingerprint == issue_fingerprint
        assert decision.plan_id == autonomous_plan.plan_id
        assert decision.plan_fingerprint == autonomous_plan.plan_fingerprint
        assert decision.server_id == SERVER_ID
        assert decision.action_type == ACTION_TYPE
        assert decision.target == SERVICE_NAME
        persisted_decision = container.autonomous_execution_service.get_decision(decision.decision_id)
        assert persisted_decision is not None
        assert persisted_decision.outcome == "auto_execute"
        assert persisted_decision.plan_id == autonomous_plan.plan_id

        acceptance_key = f"phase7-real-autonomous-{autonomous_plan.plan_id}"
        attempt = container.autonomous_execution_service.attempt(
            plan_id=autonomous_plan.plan_id,
            actor=ACCEPTANCE_ACTOR,
            idempotency_key=acceptance_key,
        )
        assert attempt["outcome"] == "auto_execute"
        assert attempt["decision"].outcome.value == "auto_execute"
        execution_result = attempt["result"]
        assert execution_result["applied"] is True
        execution_id = execution_result["execution_id"]
        execution = container.remediation_repository.get_execution(execution_id=execution_id)
        assert execution is not None
        assert execution.status == "succeeded"
        assert execution.execution_metadata.get("autonomous") is True
        assert execution.before_evidence_ids
        assert execution.after_evidence_ids
        active = container.remediation_repository.get_evidence(execution.after_evidence_ids[0])
        assert active is not None
        assert active.plan_id == autonomous_plan.plan_id
        assert active.execution_id == execution.execution_id
        assert active.server_id == SERVER_ID
        assert active.service == SERVICE_NAME
        assert active.observed_state == "active"
        autonomous_plan_after = container.remediation_service.get_plan(autonomous_plan.plan_id)
        assert autonomous_plan_after.execution_status == "succeeded"
        assert autonomous_plan_after.verification_status == "verified"

        authorization_id = attempt["authorization_id"]
        authorization = container.autonomous_remediation_repository.get_authorization(authorization_id)
        assert authorization is not None
        assert authorization.status == "consumed"
        assert authorization.policy_id == policy.policy_id
        assert authorization.policy_version == policy.version
        assert authorization.decision_id == attempt["decision"].decision_id
        assert authorization.plan_id == autonomous_plan.plan_id
        assert authorization.plan_fingerprint == autonomous_plan.plan_fingerprint
        assert authorization.server_id == SERVER_ID
        assert authorization.action_type == ACTION_TYPE
        assert authorization.target == SERVICE_NAME
        assert authorization.sandbox_validation_id == sandbox.validation_id
        with pytest.raises(ValueError, match="not valid"):
            container.autonomous_authorization_service.consume(authorization_id)

        reservations = container.autonomous_execution_service.list_reservations(
            plan_id=autonomous_plan.plan_id,
            limit=10,
        )
        assert len(reservations) == 1
        reservation = reservations[0]
        assert reservation.status == "completed"
        assert reservation.policy_id == policy.policy_id
        assert reservation.plan_id == autonomous_plan.plan_id
        assert reservation.plan_fingerprint == autonomous_plan.plan_fingerprint
        assert reservation.action_type == ACTION_TYPE
        assert reservation.target == SERVICE_NAME
        assert reservation.server_id == SERVER_ID
        assert reservation.execution_id == execution_id
        assert reservation.authorization_id == authorization_id

        audit_events = container.remediation_service.list_audit_events(autonomous_plan.plan_id)
        audit_types = {event.event_type for event in audit_events}
        assert {
            "autonomous_policy_evaluated",
            "autonomous_execution_reserved",
            "autonomous_authorization_issued",
            "autonomous_authorization_consumed",
            "execution_started",
            "execution_succeeded",
            "autonomous_execution_finalized",
        }.issubset(audit_types)

        duplicate = container.autonomous_execution_service.attempt(
            plan_id=autonomous_plan.plan_id,
            actor=ACCEPTANCE_ACTOR,
            idempotency_key=acceptance_key,
        )
        assert duplicate.get("idempotent") is True
        assert duplicate["reservation"]["reservation_id"] == reservation.reservation_id
        assert len(
            container.remediation_repository.list_evidence(
                plan_id=autonomous_plan.plan_id,
                execution_id=execution_id,
            )
        ) >= 2
        assert container.remediation_repository.get_execution(
            idempotency_key=acceptance_key
        ).execution_id == execution_id

        result = {
            "issue_fingerprint": issue_fingerprint,
            "history": {
                "supervised_execution_count": history.supervised_execution_count,
                "verified_success_count": history.verified_success_count,
                "failed_execution_count": history.failed_execution_count,
            },
            "candidate_eligible": True,
            "policy_id": policy.policy_id,
            "policy_version": policy.version,
            "autonomous_plan_id": autonomous_plan.plan_id,
            "autonomous_plan_fingerprint": autonomous_plan.plan_fingerprint,
            "sandbox_validation_id": sandbox.validation_id,
            "decision_id": attempt["decision"].decision_id,
            "decision_outcome": attempt["decision"].outcome.value,
            "authorization_id": authorization.authorization_id,
            "authorization_status": authorization.status,
            "reservation_id": reservation.reservation_id,
            "execution_id": execution.execution_id,
            "execution_status": execution.status,
            "verification_status": autonomous_plan_after.verification_status,
            "idempotent_reexecution_blocked": True,
        }
    except Exception as exc:
        original_error = exc
        raise
    finally:
        cleanup_errors = _restore_active_plans(container, plan_ids)
        if policy_id is not None:
            try:
                disabled = container.autonomous_policy_service.disable(policy_id)
                if disabled.status != "disabled":
                    cleanup_errors.append(f"policy {policy_id}: disable did not persist")
            except Exception as exc:  # pragma: no cover - real cleanup diagnostics
                cleanup_errors.append(
                    f"policy {policy_id}: {type(exc).__name__}: {exc}"
                )
        if cleanup_errors:
            message = {
                "cleanup_errors": cleanup_errors,
                "original_error": str(original_error) if original_error else None,
            }
            print(json.dumps(message, default=str), file=sys.stderr)
            if original_error is None:
                pytest.fail(
                    "PHASE7_REAL_ACCEPTANCE = CLEANUP_FAILED: "
                    + "; ".join(cleanup_errors)
                )

    result["final_policy_status"] = "disabled"
    result["final_state_restored"] = True
    print(json.dumps(result, sort_keys=True, default=str))
