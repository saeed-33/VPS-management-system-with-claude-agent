from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.capabilities.remediation.execution import WriteCommandResult
from app.capabilities.remediation.service import RemediationService
from app.core.contracts.remediation import RemediationPlanStatus
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.remediation import (
    RemediationApprovalModel,
    RemediationAuditEventModel,
    RemediationExecutionModel,
    RemediationPlanModel,
    RemediationRollbackModel,
    RemediationSandboxResultModel,
    RemediationVerificationModel,
)
from app.infrastructure.database.repositories.remediation_repository import RemediationRepository


class FakeWriter:
    def __init__(self, result: WriteCommandResult | None = None):
        self.calls = []
        self.result = result or WriteCommandResult(success=True, exit_status=0, stdout="ok")

    def run(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class FakeVerifier:
    def __init__(self, verified=True):
        self.verified = verified

    def verify(self, **_kwargs):
        return self.verified, {"state": "active" if self.verified else "unknown"}


def make_service(*, writer=None, verifier=None):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            RemediationPlanModel.__table__,
            RemediationSandboxResultModel.__table__,
            RemediationApprovalModel.__table__,
            RemediationExecutionModel.__table__,
            RemediationVerificationModel.__table__,
            RemediationRollbackModel.__table__,
            RemediationAuditEventModel.__table__,
        ],
    )
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    return RemediationService(
        repository=RemediationRepository(factory),
        write_runner=writer or FakeWriter(),
        verification_runner=verifier or FakeVerifier(),
    )


def make_plan(service, *, action=None, server_id=7):
    return service.create_plan(
        plan_id="phase5-plan",
        investigation_id="inv-1",
        title="Bounded service action",
        problem_summary="The service needs a controlled restart.",
        proposed_actions=[action or {
            "id": "start-nginx",
            "action_type": "start_service",
            "target": "nginx",
            "reason": "Restore the named service.",
        }],
        diagnosis_claim_ids=["claim-1"],
        evidence_ids=["evidence-1"],
        server_id=server_id,
    )


def approve_plan(service, plan_id="phase5-plan"):
    make_plan(service, server_id=7)
    service.test_in_sandbox(plan_id=plan_id)
    approval = service.request_approval(plan_id=plan_id)
    service.approve(approval_id=approval.approval_id, approver="human-operator")
    return approval


def test_raw_command_and_unknown_write_tool_are_rejected():
    service = make_service()
    try:
        make_plan(service, action={"id": "raw", "description": "bad", "command": "systemctl start nginx"})
    except ValueError as exc:
        assert "Raw command" in str(exc)
    else:
        raise AssertionError("raw command was accepted")

    plan = make_plan(service, action={"id": "unknown", "action_type": "delete_database", "target": "db", "reason": "bad"})
    result = service.test_in_sandbox(plan_id=plan.plan_id)
    assert result.status == "failed"

    for malicious_target in (
        "nginx; reboot", "nginx && whoami", "$(whoami)", "`whoami`",
        "nginx | cat /etc/passwd", "../something", "nginx\nwhoami",
    ):
        injected = make_service()
        plan = make_plan(injected, action={
            "id": "injected", "action_type": "start_service",
            "target": malicious_target, "reason": "bad",
        })
        assert injected.test_in_sandbox(plan_id=plan.plan_id).status == "failed"


def test_supervised_execution_rechecks_approval_server_and_idempotency():
    writer = FakeWriter()
    service = make_service(writer=writer)
    approval = approve_plan(service)
    outcome = service.apply_approved(plan_id="phase5-plan", approval_id=approval.approval_id, server_id=7, actor="human-operator")
    assert outcome["applied"] is True
    assert writer.calls[0]["command"] == "systemctl start nginx"
    assert "command_text" not in writer.calls[0]

    again = service.apply_approved(plan_id="phase5-plan", approval_id=approval.approval_id, server_id=7, actor="human-operator")
    assert again["idempotent"] is True
    assert len(writer.calls) == 1

    wrong_server = service.apply_approved(plan_id="phase5-plan", approval_id=approval.approval_id, server_id=8, actor="human-operator")
    assert wrong_server["applied"] is False


def test_rejected_and_expired_approval_cannot_execute():
    service = make_service()
    service.test_in_sandbox(plan_id=make_plan(service).plan_id)
    approval = service.request_approval(plan_id="phase5-plan")
    service.reject(approval_id=approval.approval_id, approver="human-operator", comment="not safe")
    result = service.apply_approved(plan_id="phase5-plan", approval_id=approval.approval_id, server_id=7)
    assert result["blocked_reason"] == "approval_rejected"

    service2 = make_service()
    make_plan(service2)
    service2.test_in_sandbox(plan_id="phase5-plan")
    expired = service2.request_approval(plan_id="phase5-plan", expires_in_seconds=-1)
    service2.expire_approval(approval_id=expired.approval_id)
    result = service2.apply_approved(plan_id="phase5-plan", approval_id=expired.approval_id, server_id=7)
    assert result["applied"] is False


def test_execution_and_verification_failures_are_not_reported_as_success():
    failed_writer = FakeWriter(WriteCommandResult(success=False, exit_status=1, stderr="failed", error="nonzero"))
    failed = make_service(writer=failed_writer)
    approval = approve_plan(failed)
    outcome = failed.apply_approved(plan_id="phase5-plan", approval_id=approval.approval_id, server_id=7)
    assert outcome["blocked_reason"] == "execution_failed"
    assert failed.get_plan("phase5-plan").status == RemediationPlanStatus.ROLLBACK_REQUIRED.value

    unverified = make_service(verifier=FakeVerifier(verified=False))
    approval = approve_plan(unverified)
    outcome = unverified.apply_approved(plan_id="phase5-plan", approval_id=approval.approval_id, server_id=7)
    assert outcome["blocked_reason"] == "verification_failed"
    assert unverified.get_plan("phase5-plan").verification_status == "failed"


def test_rollback_uses_only_registered_reverse_action_and_records_evidence():
    writer = FakeWriter()
    service = make_service(writer=writer)
    approval = approve_plan(service)
    outcome = service.apply_approved(plan_id="phase5-plan", approval_id=approval.approval_id, server_id=7)
    rollback = service.rollback(plan_id="phase5-plan", execution_id=outcome["execution_id"], server_id=7, actor="human-operator")
    assert rollback["rolled_back"] is True
    assert writer.calls[-1]["command"] == "systemctl stop nginx"


def test_rollback_failure_is_explicit_and_not_hidden():
    writer = FakeWriter(WriteCommandResult(success=False, exit_status=1, error="rollback ssh failure"))
    service = make_service(writer=writer)
    approval = approve_plan(service)
    outcome = service.apply_approved(plan_id="phase5-plan", approval_id=approval.approval_id, server_id=7)
    rollback = service.rollback(plan_id="phase5-plan", execution_id=outcome["execution_id"], server_id=7, actor="human-operator")
    assert rollback["rolled_back"] is False
    assert service.get_plan("phase5-plan").status == RemediationPlanStatus.ROLLBACK_FAILED.value


def test_no_solution_found_is_a_persisted_normal_outcome():
    service = make_service()
    plan = service.record_no_solution_found(
        investigation_id="inv-2", title="No safe action", problem_summary="Evidence was insufficient.",
        diagnosis_claim_ids=["claim-2"], evidence_ids=["evidence-2"], server_id=7,
    )
    assert plan.status == RemediationPlanStatus.NO_SOLUTION_FOUND.value
    assert plan.proposed_actions == []
