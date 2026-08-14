from datetime import datetime, timezone

import pytest

from tests.test_autonomous_remediation_policy import context
from app.core.contracts.autonomous_remediation import AutonomousDecisionOutcome
from app.core.policies.autonomous_remediation import AutonomousRemediationPolicyEvaluator


@pytest.mark.parametrize(
    ("classification", "reason"),
    [
        ("dangerous", "dangerous_error_classification"),
        ("sensitive", "sensitive_error_classification"),
    ],
)
def test_dangerous_or_sensitive_classification_cannot_auto_execute(
    classification,
    reason,
):
    decision = AutonomousRemediationPolicyEvaluator().evaluate(
        context(error_classification=classification)
    )
    assert decision.outcome is AutonomousDecisionOutcome.DENY
    assert decision.reason_codes == (reason,)
    assert decision.metadata["error_classification"] == classification
