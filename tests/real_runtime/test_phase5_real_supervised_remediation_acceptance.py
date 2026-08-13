from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid4

import pytest

from app.core.policies.remediation_tools import SERVICE_NAME_RE
from app.core.contracts.sandbox_validation import SandboxRuntimeCheck


RUN_REAL_ACCEPTANCE = os.getenv("REAL_PHASE5_ACCEPTANCE_ENABLED", "").strip().lower() == "true"

pytestmark = pytest.mark.skipif(
    not RUN_REAL_ACCEPTANCE,
    reason="Real Phase 5 acceptance is opt-in; set REAL_PHASE5_ACCEPTANCE_ENABLED=true.",
)


def _restore_operational_runtime_env() -> None:
    from dotenv import dotenv_values

    env_path = Path(__file__).resolve().parents[2] / ".env"
    values = dotenv_values(env_path)

    required = (
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "SSH_KNOWN_HOSTS_PATH",
    )
    optional = (
        "DEFAULT_SSH_PRIVATE_KEY_PATH",
    )

    missing = [
        key
        for key in required
        if not str(values.get(key) or "").strip()
    ]
    if missing:
        pytest.fail(
            "REAL_PHASE5_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: missing "
            + ", ".join(missing)
        )

    for key in (*required, *optional):
        value = str(values.get(key) or "").strip()
        if value:
            os.environ[key] = value


def _safe_target():
    raw_id = os.getenv("SAFE_REMEDIATION_SERVER_ID", "").strip()
    expected_name = os.getenv("SAFE_REMEDIATION_SERVER_NAME", "").strip()
    service = os.getenv("SAFE_REMEDIATION_SERVICE", "").strip()
    if not raw_id or not expected_name or not service:
        pytest.fail(
            "REAL_PHASE5_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: "
            "SAFE_REMEDIATION_SERVER_ID, SAFE_REMEDIATION_SERVER_NAME, and SAFE_REMEDIATION_SERVICE are required."
        )
    try:
        server_id = int(raw_id)
    except ValueError:
        pytest.fail("REAL_PHASE5_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: server ID must be an integer.")
    if server_id < 1 or not SERVICE_NAME_RE.fullmatch(service):
        pytest.fail("REAL_PHASE5_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: safe service identifier is invalid.")
    return server_id, expected_name, service


def test_phase5_real_supervised_remediation_acceptance():
    _restore_operational_runtime_env()
    server_id, expected_name, service_name = _safe_target()

    from app.composition import container
    server = container.server_repository.get_by_id(server_id)
    if server is None or server.name != expected_name:
        pytest.fail("REAL_PHASE5_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: explicit server binding failed.")

    designation = (server.description or "").casefold()
    required_markers = ("safe-remediation-test", "non-production")
    if not all(marker in designation for marker in required_markers):
        pytest.fail(
            "REAL_PHASE5_ACCEPTANCE = BLOCKED_BY_SAFE_TEST_ENVIRONMENT: "
            "server description must explicitly contain safe-remediation-test and non-production."
        )

    service = container.remediation_service
    plan_id = f"phase5-real-{uuid4().hex}"
    plan = service.create_plan(
        plan_id=plan_id,
        investigation_id=f"phase5-real-investigation-{uuid4().hex}",
        title="Safe supervised remediation acceptance",
        problem_summary="Dedicated harmless test service is intentionally inactive.",
        proposed_actions=[{
            "id": "start-safe-remediation-service",
            "action_type": "start_service",
            "target": service_name,
            "reason": "Restore the dedicated acceptance service.",
        }],
        diagnosis_claim_ids=["phase5-real-diagnosis"],
        evidence_ids=["phase5-real-context"],
        server_id=server_id,
    )

    preflight = service.collect_service_evidence(
        plan_id=plan.plan_id, server_id=server_id, service=service_name,
    )
    assert preflight.observed_state == "inactive", "Acceptance target must start inactive; no write was attempted."

    # Phase 5's accepted real-server workflow now crosses the Phase 6
    # fingerprint-bound approval gate. This compatibility acceptance supplies
    # an explicit runtime check; native Claude sandbox acceptance is covered
    # separately by the opt-in Phase 6 test.
    sandbox = service.validate_in_isolated_sandbox(
        plan_id=plan.plan_id,
        target_server_id=server_id,
        target_server_name=expected_name,
        target_service=service_name,
        runtime_check=SandboxRuntimeCheck(
            available=True,
            runtime="phase5-accepted-real-runtime",
            evidence={"phase5_compatibility": True},
        ),
    )
    assert sandbox.status == "passed"
    approval_request = service.request_approval(plan_id=plan.plan_id)
    approval = service.approve(approval_id=approval_request.approval_id, approver="phase5-acceptance-operator")

    execution_outcome = None
    rollback_outcome = None
    try:
        execution_outcome = service.apply_approved(
            plan_id=plan.plan_id,
            approval_id=approval.approval_id,
            server_id=server_id,
            actor="phase5-acceptance-operator",
            idempotency_key=f"{plan.plan_id}:start",
        )
        assert execution_outcome["applied"] is True
        execution = service.get_latest_execution(plan.plan_id)
        assert execution is not None
        before = service._repository.get_evidence(execution.before_evidence_ids[0])
        after = service._repository.get_evidence(execution.after_evidence_ids[0])
        assert before is not None and before.observed_state == "inactive"
        assert after is not None and after.observed_state == "active"

        duplicate = service.apply_approved(
            plan_id=plan.plan_id, approval_id=approval.approval_id,
            server_id=server_id, actor="phase5-acceptance-operator",
            idempotency_key=f"{plan.plan_id}:start",
        )
        assert duplicate["idempotent"] is True
        assert duplicate["execution"].execution_id == execution.execution_id

        rollback_outcome = service.rollback(
            plan_id=plan.plan_id, execution_id=execution.execution_id,
            server_id=server_id, actor="phase5-acceptance-operator",
        )
        assert rollback_outcome["rolled_back"] is True
        rollback = service._repository.get_rollback(rollback_outcome["rollback_id"])
        assert rollback is not None
        final = service._repository.get_evidence(rollback.after_evidence_ids[0])
        assert final is not None and final.observed_state == "inactive"

        events = service.list_audit_events(plan.plan_id)
        event_types = [event.event_type for event in events]
        assert {"approval_granted", "execution_started", "execution_succeeded", "rollback_succeeded"}.issubset(event_types)
        print(json.dumps({
            "status": "accepted",
            "plan_id": plan.plan_id,
            "server_id": server_id,
            "server_name": server.name,
            "service": service_name,
            "risk": plan.risk_level,
            "fingerprint": plan.plan_fingerprint,
            "approval_id": approval.approval_id,
            "approval_actor": approval.approver,
            "execution_id": execution.execution_id,
            "before_evidence_ids": execution.before_evidence_ids,
            "after_evidence_ids": execution.after_evidence_ids,
            "rollback_id": rollback.rollback_id,
            "rollback_before_evidence_ids": rollback.before_evidence_ids,
            "rollback_after_evidence_ids": rollback.after_evidence_ids,
            "audit_event_ids": [event.event_id for event in events],
            "automatic_remediation_allowed": False,
        }, indent=2, default=str))
    finally:
        # If a failure occurs after a successful write but before the explicit
        # rollback, use the same policy-protected rollback path for recovery.
        if execution_outcome and execution_outcome.get("applied") and rollback_outcome is None:
            execution = service.get_latest_execution(plan.plan_id)
            if execution is not None:
                service.rollback(plan_id=plan.plan_id, execution_id=execution.execution_id,
                                 server_id=server_id, actor="phase5-acceptance-recovery")
