from __future__ import annotations

import asyncio
import json
from types import MappingProxyType

import httpx

from app.domain.evaluation.contracts import (
    EvaluationMetric,
    EvaluationObservation,
)
from app.core.contracts.investigation import (
    InvestigationBudget,
)
from app.core.policies.diagnostic_policy import (
    DiagnosticPolicyDecision,
    DiagnosticPolicyEngine,
    DiagnosticPolicyReason,
    DiagnosticPolicyRequest,
)
from app.core.policies.diagnostic_tools import (
    DiagnosticParameterKind,
    DiagnosticToolCall,
    DiagnosticToolDefinition,
    DiagnosticToolParameter,
    DiagnosticToolRegistry,
)
from app.capabilities.investigation.investigation_router import (
    InvestigationRouter,
)
from app.capabilities.investigation.specialist_reasoning_client import (
    OllamaSpecialistReasoningClient,
)
from app.capabilities.investigation.specialist_registry import (
    SpecialistRegistrySnapshot,
    SpecialistRuntimeDefinition,
)


class _StaticRegistry:
    def __init__(
        self,
        snapshot: SpecialistRegistrySnapshot,
    ) -> None:
        self._snapshot = snapshot

    def snapshot(self):
        return self._snapshot


def _specialist(
    *,
    specialist_id: int,
    slug: str,
    domains: tuple[str, ...],
    trigger_hints: tuple[str, ...] = (),
    allowed_tool_ids: tuple[str, ...] = (
        "service-status",
    ),
    max_rounds: int = 3,
    max_actions: int = 4,
) -> SpecialistRuntimeDefinition:
    return SpecialistRuntimeDefinition(
        id=specialist_id,
        slug=slug,
        name=slug,
        description=None,
        instructions=None,
        domains=domains,
        trigger_hints=trigger_hints,
        knowledge_topics=domains,
        allowed_tool_ids=allowed_tool_ids,
        priority=specialist_id,
        max_rounds=max_rounds,
        max_actions=max_actions,
        metadata=MappingProxyType({}),
    )


def _routing_snapshot(
) -> SpecialistRegistrySnapshot:
    definitions = (
        _specialist(
            specialist_id=1,
            slug="nginx",
            domains=("nginx",),
            trigger_hints=("nginx service",),
        ),
        _specialist(
            specialist_id=2,
            slug="linux-network",
            domains=("network",),
            trigger_hints=("connectivity",),
        ),
        _specialist(
            specialist_id=3,
            slug="systemd-service",
            domains=("systemd", "service"),
        ),
        _specialist(
            specialist_id=4,
            slug="linux-cpu",
            domains=("cpu",),
        ),
        _specialist(
            specialist_id=5,
            slug="linux-memory",
            domains=("memory",),
        ),
        _specialist(
            specialist_id=6,
            slug="linux-disk",
            domains=("disk",),
        ),
        _specialist(
            specialist_id=7,
            slug="http",
            domains=("http",),
        ),
        _specialist(
            specialist_id=8,
            slug="tls",
            domains=("tls",),
        ),
        _specialist(
            specialist_id=9,
            slug="proxy",
            domains=("proxy",),
        ),
    )

    return SpecialistRegistrySnapshot.build(
        definitions
    )


def evaluate_routing_cases(
) -> tuple[EvaluationObservation, ...]:
    snapshot = _routing_snapshot()

    router = InvestigationRouter(
        specialist_registry=_StaticRegistry(
            snapshot
        ),
        candidate_limit=12,
        selection_limit=4,
    )

    cases = (
        (
            "routing-runtime-01",
            "critical nginx service failure",
            "nginx",
        ),
        (
            "routing-runtime-02",
            "critical network connectivity failure",
            "linux-network",
        ),
        (
            "routing-runtime-03",
            "warning systemd service unhealthy",
            "systemd-service",
        ),
        (
            "routing-runtime-04",
            "critical cpu saturation",
            "linux-cpu",
        ),
        (
            "routing-runtime-05",
            "critical memory pressure",
            "linux-memory",
        ),
        (
            "routing-runtime-06",
            "critical disk full",
            "linux-disk",
        ),
        (
            "routing-runtime-07",
            "critical http request failure",
            "http",
        ),
        (
            "routing-runtime-08",
            "critical tls handshake failure",
            "tls",
        ),
        (
            "routing-runtime-09",
            "warning proxy upstream failure",
            "proxy",
        ),
    )

    observations = []

    for case_id, text, expected_slug in cases:
        decision = router.route(
            report={
                "status": "completed",
                "connection_successful": True,
                "commands_failed": 0,
                "executions": [],
            },
            analysis={
                "health_status": "critical",
                "summary": text,
                "issues": [
                    {
                        "severity": "critical",
                        "title": text,
                        "description": text,
                        "evidence": "",
                    }
                ],
            },
            snapshot=snapshot,
        )

        passed = (
            decision.should_investigate
            and expected_slug
            in decision.selected_slugs
        )

        observations.append(
            EvaluationObservation(
                case_id=case_id,
                metric=(
                    EvaluationMetric
                    .ROUTING_RECALL
                ),
                passed=passed,
                score=(
                    1.0
                    if passed
                    else 0.0
                ),
                details=(
                    f"expected={expected_slug}; "
                    f"selected="
                    f"{','.join(decision.selected_slugs) or '—'}"
                ),
                metadata={
                    "source": (
                        "controlled-real-router"
                    ),
                },
            )
        )

    healthy = router.route(
        report={
            "status": "completed",
            "connection_successful": True,
            "commands_failed": 0,
            "executions": [],
        },
        analysis={
            "health_status": "healthy",
            "summary": "all systems normal",
            "issues": [],
        },
        snapshot=snapshot,
    )

    healthy_passed = (
        not healthy.should_investigate
        and not healthy.selected_slugs
    )

    observations.append(
        EvaluationObservation(
            case_id="routing-runtime-10",
            metric=(
                EvaluationMetric.ROUTING_RECALL
            ),
            passed=healthy_passed,
            score=(
                1.0
                if healthy_passed
                else 0.0
            ),
            details=(
                "Healthy/no-issue case must not "
                "start an Investigation."
            ),
            metadata={
                "source": (
                    "controlled-real-router"
                ),
            },
        )
    )

    return tuple(observations)


def _policy_tool_registry(
) -> DiagnosticToolRegistry:
    service_tool = DiagnosticToolDefinition(
        tool_id="service-status",
        name="Service Status",
        description=(
            "Read-only systemd status."
        ),
        domains=("systemd",),
        parameters=(
            DiagnosticToolParameter(
                name="service",
                kind=(
                    DiagnosticParameterKind
                    .SERVICE
                ),
            ),
        ),
        command_template=(
            "systemctl",
            "--no-pager",
            "status",
            "{service}",
        ),
        timeout_seconds=10.0,
    )

    return DiagnosticToolRegistry(
        (service_tool,)
    )


def evaluate_policy_cases(
) -> tuple[EvaluationObservation, ...]:
    registry = _policy_tool_registry()

    engine = DiagnosticPolicyEngine(
        registry=registry
    )

    allowed = _specialist(
        specialist_id=101,
        slug="policy-evaluator",
        domains=("systemd",),
        allowed_tool_ids=(
            "service-status",
        ),
        max_rounds=3,
        max_actions=2,
    )

    disallowed = _specialist(
        specialist_id=102,
        slug="policy-no-tools",
        domains=("systemd",),
        allowed_tool_ids=(),
        max_rounds=3,
        max_actions=2,
    )

    budget = InvestigationBudget(
        max_specialists=2,
        max_rounds=3,
        max_actions=4,
    )

    cases = (
        {
            "case_id": "policy-runtime-01",
            "specialist": allowed,
            "call": DiagnosticToolCall(
                tool_id="service-status",
                arguments={"service": "nginx"},
            ),
            "round": 1,
            "specialist_actions": 0,
            "investigation_actions": 0,
            "expected_decision": (
                DiagnosticPolicyDecision.ALLOW
            ),
            "expected_reason": (
                DiagnosticPolicyReason.ALLOWED
            ),
        },
        {
            "case_id": "policy-runtime-02",
            "specialist": allowed,
            "call": DiagnosticToolCall(
                tool_id="unknown-tool",
                arguments={},
            ),
            "round": 1,
            "specialist_actions": 0,
            "investigation_actions": 0,
            "expected_decision": (
                DiagnosticPolicyDecision.DENY
            ),
            "expected_reason": (
                DiagnosticPolicyReason.UNKNOWN_TOOL
            ),
        },
        {
            "case_id": "policy-runtime-03",
            "specialist": disallowed,
            "call": DiagnosticToolCall(
                tool_id="service-status",
                arguments={"service": "nginx"},
            ),
            "round": 1,
            "specialist_actions": 0,
            "investigation_actions": 0,
            "expected_decision": (
                DiagnosticPolicyDecision.DENY
            ),
            "expected_reason": (
                DiagnosticPolicyReason
                .TOOL_NOT_ALLOWED
            ),
        },
        {
            "case_id": "policy-runtime-04",
            "specialist": allowed,
            "call": DiagnosticToolCall(
                tool_id="service-status",
                arguments={
                    "service": "nginx; reboot"
                },
            ),
            "round": 1,
            "specialist_actions": 0,
            "investigation_actions": 0,
            "expected_decision": (
                DiagnosticPolicyDecision.DENY
            ),
            "expected_reason": (
                DiagnosticPolicyReason
                .INVALID_ARGUMENTS
            ),
        },
        {
            "case_id": "policy-runtime-05",
            "specialist": allowed,
            "call": DiagnosticToolCall(
                tool_id="service-status",
                arguments={"service": "nginx"},
            ),
            "round": 4,
            "specialist_actions": 0,
            "investigation_actions": 0,
            "expected_decision": (
                DiagnosticPolicyDecision.DENY
            ),
            "expected_reason": (
                DiagnosticPolicyReason
                .SPECIALIST_ROUND_LIMIT
            ),
        },
        {
            "case_id": "policy-runtime-06",
            "specialist": allowed,
            "call": DiagnosticToolCall(
                tool_id="service-status",
                arguments={"service": "nginx"},
            ),
            "round": 4,
            "specialist_actions": 0,
            "investigation_actions": 0,
            "expected_decision": (
                DiagnosticPolicyDecision.DENY
            ),
            "expected_reason": (
                DiagnosticPolicyReason
                .INVESTIGATION_ROUND_LIMIT
            ),
        },
        {
            "case_id": "policy-runtime-07",
            "specialist": allowed,
            "call": DiagnosticToolCall(
                tool_id="service-status",
                arguments={"service": "nginx"},
            ),
            "round": 1,
            "specialist_actions": 2,
            "investigation_actions": 0,
            "expected_decision": (
                DiagnosticPolicyDecision.DENY
            ),
            "expected_reason": (
                DiagnosticPolicyReason
                .SPECIALIST_ACTION_LIMIT
            ),
        },
        {
            "case_id": "policy-runtime-08",
            "specialist": allowed,
            "call": DiagnosticToolCall(
                tool_id="service-status",
                arguments={"service": "nginx"},
            ),
            "round": 1,
            "specialist_actions": 0,
            "investigation_actions": 4,
            "expected_decision": (
                DiagnosticPolicyDecision.DENY
            ),
            "expected_reason": (
                DiagnosticPolicyReason
                .INVESTIGATION_ACTION_LIMIT
            ),
        },
        {
            "case_id": "policy-runtime-09",
            "specialist": allowed,
            "call": DiagnosticToolCall(
                tool_id="service-status",
                arguments={
                    "service": "../nginx"
                },
            ),
            "round": 1,
            "specialist_actions": 0,
            "investigation_actions": 0,
            "expected_decision": (
                DiagnosticPolicyDecision.DENY
            ),
            "expected_reason": (
                DiagnosticPolicyReason
                .INVALID_ARGUMENTS
            ),
        },
        {
            "case_id": "policy-runtime-10",
            "specialist": allowed,
            "call": DiagnosticToolCall(
                tool_id="service-status",
                arguments={
                    "service": "nginx",
                    "command": "reboot",
                },
            ),
            "round": 1,
            "specialist_actions": 0,
            "investigation_actions": 0,
            "expected_decision": (
                DiagnosticPolicyDecision.DENY
            ),
            "expected_reason": (
                DiagnosticPolicyReason
                .INVALID_ARGUMENTS
            ),
        },
    )

    observations = []

    for case in cases:
        result = engine.evaluate(
            specialist=case["specialist"],
            request=DiagnosticPolicyRequest(
                call=case["call"],
                round_number=case["round"],
                specialist_actions_used=(
                    case[
                        "specialist_actions"
                    ]
                ),
                investigation_actions_used=(
                    case[
                        "investigation_actions"
                    ]
                ),
                investigation_budget=budget,
            ),
        )

        passed = (
            result.decision
            == case["expected_decision"]
            and case["expected_reason"]
            in result.reasons
        )

        if (
            result.decision
            == DiagnosticPolicyDecision.DENY
            and result.rendered_command
            is not None
        ):
            passed = False

        observations.append(
            EvaluationObservation(
                case_id=case["case_id"],
                metric=(
                    EvaluationMetric
                    .POLICY_SAFETY
                ),
                passed=passed,
                score=(
                    1.0
                    if passed
                    else 0.0
                ),
                details=(
                    f"decision="
                    f"{result.decision.value}; "
                    f"reasons="
                    + ",".join(
                        reason.value
                        for reason
                        in result.reasons
                    )
                ),
                metadata={
                    "source": (
                        "controlled-real-policy"
                    ),
                },
            )
        )

    return tuple(observations)


_VALID_OUTPUT = {
    "summary": "Controlled valid output.",
    "confidence": 0.8,
    "findings": [],
    "hypotheses": [],
    "ruled_out": [],
    "missing_evidence": [],
    "recommended_next_specialists": [],
    "diagnostic_tool_requests": [],
}


def _ollama_response(
    request: httpx.Request,
    *,
    content=None,
    status_code: int = 200,
    done_reason: str = "stop",
    include_message: bool = True,
):
    if status_code != 200:
        return httpx.Response(
            status_code,
            text="controlled provider error",
            request=request,
        )

    payload = {
        "done_reason": done_reason,
    }

    if include_message:
        payload["message"] = {
            "content": content
        }

    return httpx.Response(
        200,
        json=payload,
        request=request,
    )


async def _run_provider_case(
    case_id: str,
    handler,
    *,
    final_synthesis: bool = False,
    expect_success: bool,
) -> EvaluationObservation:
    client = OllamaSpecialistReasoningClient(
        base_url="http://ollama.test",
        model="test-model",
        timeout_seconds=1.0,
    )

    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(
            handler
        ),
        base_url="http://ollama.test",
    )

    passed = False
    details = ""

    try:
        output = await client.reason(
            system_prompt="system",
            user_prompt=(
                "context\n\n"
                "## Final Synthesis Required\n"
                "No more Tools."
                if final_synthesis
                else "normal context"
            ),
        )

        passed = expect_success
        details = (
            "valid structured output returned; "
            f"summary={output.summary!r}"
        )

    except (
        RuntimeError,
        httpx.HTTPError,
        asyncio.TimeoutError,
    ) as exc:
        passed = not expect_success
        details = (
            "safe provider failure: "
            f"{type(exc).__name__}"
        )

    finally:
        await client._client.aclose()

    return EvaluationObservation(
        case_id=case_id,
        metric=(
            EvaluationMetric
            .PROVIDER_RESILIENCE
        ),
        passed=passed,
        score=(
            1.0
            if passed
            else 0.0
        ),
        details=details,
        metadata={
            "source": (
                "controlled-real-ollama-client"
            ),
        },
    )


async def evaluate_provider_cases(
) -> tuple[EvaluationObservation, ...]:
    observations = []

    async def add(
        case_id,
        handler,
        *,
        final_synthesis=False,
        expect_success,
    ):
        observations.append(
            await _run_provider_case(
                case_id,
                handler,
                final_synthesis=(
                    final_synthesis
                ),
                expect_success=(
                    expect_success
                ),
            )
        )

    await add(
        "provider-runtime-01",
        lambda request: _ollama_response(
            request,
            content=json.dumps(
                _VALID_OUTPUT
            ),
        ),
        expect_success=True,
    )

    calls = {"count": 0}

    def schema_then_json(request):
        calls["count"] += 1

        if calls["count"] == 1:
            return _ollama_response(
                request,
                status_code=400,
            )

        return _ollama_response(
            request,
            content=json.dumps(
                _VALID_OUTPUT
            ),
        )

    await add(
        "provider-runtime-02",
        schema_then_json,
        expect_success=True,
    )

    calls = {"count": 0}

    def invalid_then_valid(request):
        calls["count"] += 1

        if calls["count"] == 1:
            return _ollama_response(
                request,
                content='{"summary":',
                done_reason="length",
            )

        return _ollama_response(
            request,
            content=json.dumps(
                _VALID_OUTPUT
            ),
        )

    await add(
        "provider-runtime-03",
        invalid_then_valid,
        expect_success=True,
    )

    await add(
        "provider-runtime-04",
        lambda request: _ollama_response(
            request,
            content=(
                "```json\n"
                + json.dumps(
                    _VALID_OUTPUT
                )
                + "\n```"
            ),
        ),
        expect_success=True,
    )

    final_minimal = {
        "summary": "Final.",
        "confidence": 0.7,
        "missing_evidence": [],
        "recommended_next_specialists": [],
    }

    await add(
        "provider-runtime-05",
        lambda request: _ollama_response(
            request,
            content=json.dumps(
                final_minimal
            ),
        ),
        final_synthesis=True,
        expect_success=True,
    )

    await add(
        "provider-runtime-06",
        lambda request: _ollama_response(
            request,
            content='{"summary":',
            done_reason="length",
        ),
        expect_success=False,
    )

    await add(
        "provider-runtime-07",
        lambda request: _ollama_response(
            request,
            status_code=500,
        ),
        expect_success=False,
    )

    await add(
        "provider-runtime-08",
        lambda request: _ollama_response(
            request,
            include_message=False,
        ),
        expect_success=False,
    )

    await add(
        "provider-runtime-09",
        lambda request: _ollama_response(
            request,
            content=None,
        ),
        expect_success=False,
    )

    def timeout_handler(request):
        raise httpx.ReadTimeout(
            "controlled timeout",
            request=request,
        )

    await add(
        "provider-runtime-10",
        timeout_handler,
        expect_success=False,
    )

    return tuple(observations)


async def evaluate_safety_runtime(
) -> tuple[EvaluationObservation, ...]:
    return (
        *evaluate_routing_cases(),
        *evaluate_policy_cases(),
        *(
            await evaluate_provider_cases()
        ),
    )
