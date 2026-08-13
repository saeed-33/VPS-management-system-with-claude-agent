from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.contracts.autonomous_remediation import (
    AutonomousPolicyStatus,
    AutonomousRemediationPolicy,
)
from app.infrastructure.database.base import Base
from app.infrastructure.database.models import (  # noqa: F401
    AutonomousAuthorizationModel,
    AutonomousPolicyDecisionModel,
    AutonomousPolicyExecutionReservationModel,
    AutonomousPolicyRuntimeStateModel,
    AutonomousRemediationPolicyModel,
)
from app.infrastructure.database.models.remediation import (
    RemediationEvidenceModel,
    RemediationExecutionModel,
    RemediationPlanModel,
    RemediationRollbackModel,
    RemediationVerificationModel,
)
from app.infrastructure.database.repositories.autonomous_remediation_repository import AutonomousRemediationRepository


def repository():
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    for model in (
        RemediationPlanModel,
        RemediationExecutionModel,
        RemediationEvidenceModel,
        RemediationVerificationModel,
        RemediationRollbackModel,
        AutonomousRemediationPolicyModel,
        AutonomousPolicyDecisionModel,
        AutonomousAuthorizationModel,
        AutonomousPolicyExecutionReservationModel,
        AutonomousPolicyRuntimeStateModel,
    ):
        model.__table__.create(engine)
    return AutonomousRemediationRepository(sessionmaker(bind=engine, expire_on_commit=False))


def test_policy_version_updates_and_status_changes_are_persisted():
    repo = repository()
    policy = AutonomousRemediationPolicy(
        policy_id="p1", name="p1", description="test", status=AutonomousPolicyStatus.DISABLED,
        version=1, issue_fingerprint="fp", allowed_action_type="start_service", allowed_target_pattern="nginx",
    )
    repo.create_policy(policy)
    enabled = repo.update_policy("p1", updates={"status": "enabled", "name": "p1-updated"}, version=2)
    assert enabled.version == 2
    assert enabled.status == "enabled"
    assert enabled.name == "p1-updated"


def test_reservation_idempotency_and_single_use_authorization():
    from datetime import datetime, timezone, timedelta
    from app.core.contracts.autonomous_remediation import AutonomousAuthorization, AutonomousAuthorizationStatus

    repo = repository()
    now = datetime.now(timezone.utc)
    first = repo.reserve(idempotency_key="k1", owner_token="worker-1", policy_id="p1", plan_id="plan", plan_fingerprint="fp", action_type="start_service", target="nginx", server_id=4, now=now)
    second = repo.reserve(idempotency_key="k1", owner_token="worker-1", policy_id="p1", plan_id="plan", plan_fingerprint="fp", action_type="start_service", target="nginx", server_id=4, now=now)
    assert first.reservation_id == second.reservation_id

    competing = repo.reserve(idempotency_key="k2", owner_token="worker-2", policy_id="p1", plan_id="plan", plan_fingerprint="fp", action_type="start_service", target="nginx", server_id=4, now=now)
    assert competing.status == "in_progress"

    recovered = repo.reserve(idempotency_key="k3", owner_token="worker-1", policy_id="p1", plan_id="plan-2", plan_fingerprint="fp", action_type="start_service", target="nginx", server_id=4, now=now, lease_seconds=1)
    recovered_again = repo.reserve(idempotency_key="k3", owner_token="worker-2", policy_id="p1", plan_id="plan-2", plan_fingerprint="fp", action_type="start_service", target="nginx", server_id=4, now=now + timedelta(seconds=2))
    assert recovered_again.status == "reserved"
    assert recovered_again.owner_token == "worker-2"

    auth = AutonomousAuthorization(
        authorization_id="a1", token="token1", status=AutonomousAuthorizationStatus.VALID,
        policy_id="p1", policy_version=1, decision_id="d1", plan_id="plan", plan_fingerprint="fp",
        server_id=4, action_type="start_service", target="nginx", sandbox_validation_id="sv1",
        issued_at=now, expires_at=now + timedelta(minutes=5),
    )
    repo.create_authorization(auth)
    repo.consume_authorization("a1", now=now)
    try:
        repo.consume_authorization("a1", now=now)
    except ValueError as exc:
        assert "not valid" in str(exc)
    else:
        raise AssertionError("Consumed authorization was reusable.")
