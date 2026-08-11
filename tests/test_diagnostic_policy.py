from types import MappingProxyType

import pytest

from app.domain.investigation.contracts import InvestigationBudget
from app.domain.investigation.diagnostic_policy import (
    DiagnosticPolicyDecision,
    DiagnosticPolicyEngine,
    DiagnosticPolicyReason,
    DiagnosticPolicyRequest,
)
from app.domain.investigation.diagnostic_tools import (
    DiagnosticToolCall,
    build_default_diagnostic_tool_registry,
)
from app.domain.investigation.specialist_registry import (
    SpecialistRuntimeDefinition,
)


def specialist(
    *,
    allowed_tool_ids=("systemd-status", "network-listeners"),
    max_rounds=2,
    max_actions=4,
):
    return SpecialistRuntimeDefinition(
        id=1,
        slug="test-specialist",
        name="Test Specialist",
        description=None,
        instructions=None,
        domains=("systemd", "network"),
        trigger_hints=(),
        knowledge_topics=(),
        allowed_tool_ids=allowed_tool_ids,
        priority=10,
        max_rounds=max_rounds,
        max_actions=max_actions,
        metadata=MappingProxyType({}),
    )


def request(
    *,
    tool_id="systemd-status",
    arguments=None,
    round_number=1,
    specialist_actions_used=0,
    investigation_actions_used=0,
    budget=None,
):
    return DiagnosticPolicyRequest(
        call=DiagnosticToolCall(
            tool_id=tool_id,
            arguments=(
                arguments
                if arguments is not None
                else {"service": "nginx"}
            ),
        ),
        round_number=round_number,
        specialist_actions_used=specialist_actions_used,
        investigation_actions_used=investigation_actions_used,
        investigation_budget=(
            budget
            or InvestigationBudget(
                max_specialists=4,
                max_rounds=3,
                max_actions=12,
            )
        ),
    )


def engine():
    return DiagnosticPolicyEngine(
        registry=build_default_diagnostic_tool_registry()
    )


def test_policy_allows_registered_assigned_safe_tool():
    result = engine().evaluate(
        specialist=specialist(),
        request=request(),
    )

    assert result.allowed
    assert result.decision == DiagnosticPolicyDecision.ALLOW
    assert result.reasons == (
        DiagnosticPolicyReason.ALLOWED,
    )
    assert result.rendered_command.endswith("status nginx")
    assert result.timeout_seconds == 12
    assert result.output_limit_chars


def test_policy_denies_unknown_tool():
    result = engine().evaluate(
        specialist=specialist(),
        request=request(
            tool_id="arbitrary-shell",
            arguments={},
        ),
    )

    assert not result.allowed
    assert result.reasons == (
        DiagnosticPolicyReason.UNKNOWN_TOOL,
    )
    assert result.rendered_command is None


def test_policy_denies_unassigned_tool():
    result = engine().evaluate(
        specialist=specialist(
            allowed_tool_ids=("network-listeners",)
        ),
        request=request(),
    )

    assert not result.allowed
    assert (
        DiagnosticPolicyReason.TOOL_NOT_ALLOWED
        in result.reasons
    )
    assert result.rendered_command is None


def test_policy_denies_invalid_arguments():
    result = engine().evaluate(
        specialist=specialist(),
        request=request(
            arguments={"service": "nginx; id"}
        ),
    )

    assert not result.allowed
    assert result.reasons == (
        DiagnosticPolicyReason.INVALID_ARGUMENTS,
    )
    assert "Unsafe service name" in (
        result.metadata["validation_error"]
    )


def test_policy_enforces_specialist_round_limit():
    result = engine().evaluate(
        specialist=specialist(max_rounds=2),
        request=request(round_number=3),
    )

    assert not result.allowed
    assert (
        DiagnosticPolicyReason.SPECIALIST_ROUND_LIMIT
        in result.reasons
    )


def test_policy_enforces_investigation_round_limit():
    result = engine().evaluate(
        specialist=specialist(max_rounds=5),
        request=request(
            round_number=3,
            budget=InvestigationBudget(
                max_specialists=4,
                max_rounds=2,
                max_actions=12,
            ),
        ),
    )

    assert not result.allowed
    assert (
        DiagnosticPolicyReason.INVESTIGATION_ROUND_LIMIT
        in result.reasons
    )


def test_policy_enforces_specialist_action_limit():
    result = engine().evaluate(
        specialist=specialist(max_actions=4),
        request=request(specialist_actions_used=4),
    )

    assert not result.allowed
    assert (
        DiagnosticPolicyReason.SPECIALIST_ACTION_LIMIT
        in result.reasons
    )


def test_policy_enforces_investigation_action_limit():
    result = engine().evaluate(
        specialist=specialist(),
        request=request(investigation_actions_used=12),
    )

    assert not result.allowed
    assert (
        DiagnosticPolicyReason.INVESTIGATION_ACTION_LIMIT
        in result.reasons
    )


def test_policy_can_report_multiple_budget_denials():
    result = engine().evaluate(
        specialist=specialist(
            max_rounds=1,
            max_actions=1,
        ),
        request=request(
            round_number=3,
            specialist_actions_used=1,
            investigation_actions_used=2,
            budget=InvestigationBudget(
                max_specialists=4,
                max_rounds=2,
                max_actions=2,
            ),
        ),
    )

    assert result.reasons == (
        DiagnosticPolicyReason.SPECIALIST_ROUND_LIMIT,
        DiagnosticPolicyReason.INVESTIGATION_ROUND_LIMIT,
        DiagnosticPolicyReason.SPECIALIST_ACTION_LIMIT,
        DiagnosticPolicyReason.INVESTIGATION_ACTION_LIMIT,
    )


def test_policy_request_rejects_invalid_counters():
    with pytest.raises(
        ValueError,
        match="specialist_actions_used",
    ):
        request(specialist_actions_used=-1)


def test_denied_result_never_exposes_execution_envelope():
    result = engine().evaluate(
        specialist=specialist(allowed_tool_ids=()),
        request=request(),
    )

    assert result.rendered_command is None
    assert result.timeout_seconds is None
    assert result.output_limit_chars is None
