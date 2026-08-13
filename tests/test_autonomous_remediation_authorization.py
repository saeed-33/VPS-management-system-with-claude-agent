from datetime import datetime, timedelta, timezone

from app.capabilities.remediation.autonomous_authorization_service import AutonomousAuthorizationService
from app.core.contracts.autonomous_remediation import AutonomousDecisionOutcome, AutonomousPolicyDecision, AutonomousAuthorizationStatus


class Repository:
    def __init__(self):
        self.authorization = None

    def create_authorization(self, authorization):
        self.authorization = authorization

    def get_authorization(self, authorization_id):
        return self.authorization

    def consume_authorization(self, authorization_id, *, now):
        self.authorization = type("Consumed", (), {"consumed_at": now})()
        return self.authorization


def test_consumption_returns_consumed_contract_for_execution_defense_in_depth():
    repository = Repository()
    service = AutonomousAuthorizationService(repository=repository)
    now = datetime.now(timezone.utc)
    decision = AutonomousPolicyDecision(
        decision_id="d1", outcome=AutonomousDecisionOutcome.AUTO_EXECUTE,
        reason_codes=("policy_match",), human_readable_reasons=("ok",),
        policy_id="p1", policy_version=1, plan_id="plan", plan_fingerprint="fp",
        server_id=4, action_type="start_service", target="nginx", evaluated_at=now,
    )
    issued = service.issue(decision=decision, sandbox_validation_id="sv1")

    class Model:
        authorization_id = issued.authorization_id
        token = issued.token
        status = "consumed"
        policy_id = issued.policy_id
        policy_version = issued.policy_version
        decision_id = issued.decision_id
        plan_id = issued.plan_id
        plan_fingerprint = issued.plan_fingerprint
        server_id = issued.server_id
        action_type = issued.action_type
        target = issued.target
        sandbox_validation_id = issued.sandbox_validation_id
        issued_at = issued.issued_at
        expires_at = issued.expires_at
        consumed_at = now

    repository.get_authorization = lambda authorization_id: Model()
    consumed = service.consume(issued.authorization_id)
    assert consumed.status is AutonomousAuthorizationStatus.CONSUMED
