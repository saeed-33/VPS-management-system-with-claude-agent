from types import SimpleNamespace

import pytest

from app.capabilities.investigation.investigation_router import (
    InvestigationRouter,
    RoutingReason,
)
from app.capabilities.investigation.specialist_registry import SpecialistRegistry


def specialist(i, slug, *, domains, trigger_hints, priority=100):
    return SimpleNamespace(
        id=i,
        slug=slug,
        name=slug,
        description=None,
        instructions=None,
        enabled=True,
        domains=domains,
        trigger_hints=trigger_hints,
        knowledge_topics=[],
        allowed_tool_ids=[],
        priority=priority,
        max_rounds=2,
        max_actions=4,
        specialist_metadata={},
    )


class FakeRepository:
    def __init__(self, items):
        self.items = items

    def list_enabled(self):
        return [x for x in self.items if x.enabled]


def make_router(*items, candidate_limit=12, selection_limit=4):
    return InvestigationRouter(
        specialist_registry=SpecialistRegistry(
            FakeRepository(list(items))
        ),
        candidate_limit=candidate_limit,
        selection_limit=selection_limit,
    )


def report(
    *,
    status="success",
    connection_successful=True,
    commands_failed=0,
    error_message=None,
):
    return SimpleNamespace(
        status=status,
        connection_successful=connection_successful,
        commands_failed=commands_failed,
        error_message=error_message,
        executions=[],
    )


def analysis(*, health_status="healthy", issues=None, summary=""):
    return SimpleNamespace(
        health_status=health_status,
        issues=issues or [],
        summary=summary,
    )


def issue(
    title,
    *,
    severity="warning",
    description="Detected problem.",
    evidence=None,
):
    return {
        "severity": severity,
        "title": title,
        "description": description,
        "evidence": evidence,
    }


def baseline():
    return (
        specialist(
            1,
            "linux-cpu",
            domains=["cpu", "process", "performance"],
            trigger_hints=["high cpu", "cpu saturation"],
            priority=20,
        ),
        specialist(
            2,
            "linux-memory",
            domains=["memory", "process", "performance"],
            trigger_hints=["high memory", "low available memory"],
            priority=20,
        ),
        specialist(
            3,
            "linux-process",
            domains=["process", "performance"],
            trigger_hints=["runaway process"],
            priority=30,
        ),
    )


def test_healthy_report_has_no_candidates_or_selection():
    decision = make_router(*baseline()).route(
        report=report(),
        analysis=analysis(),
    )
    assert decision.should_investigate is False
    assert decision.candidate_specialists == ()
    assert decision.selected_specialists == ()
    assert RoutingReason.HEALTHY_NO_ISSUES in decision.reasons


def test_cpu_issue_has_same_candidate_and_selection():
    decision = make_router(*baseline()).route(
        report=report(),
        analysis=analysis(
            health_status="warning",
            issues=[
                issue(
                    "High CPU utilization",
                    description="High cpu and cpu saturation.",
                )
            ],
        ),
    )
    assert decision.candidate_slugs == ("linux-cpu",)
    assert decision.selected_slugs == ("linux-cpu",)


def test_connection_failure_routes_network_only():
    network = specialist(
        4,
        "linux-network",
        domains=["network", "connectivity"],
        trigger_hints=["connection failed", "network unreachable"],
        priority=20,
    )
    cpu, memory, _ = baseline()

    decision = make_router(
        network,
        cpu,
        memory,
    ).route(
        report=report(
            status="connection_failed",
            connection_successful=False,
            error_message="Connect call failed ('192.168.127.142', 22)",
        ),
        analysis=analysis(
            health_status="critical",
            summary="Investigate network path and SSH service.",
            issues=[
                issue(
                    "Connection Failure to Target Server",
                    severity="critical",
                    description="Unable to connect to the server.",
                )
            ],
        ),
    )

    assert decision.candidate_slugs == ("linux-network",)
    assert decision.selected_slugs == ("linux-network",)


def test_candidate_shortlist_can_exceed_selection_budget():
    items = [
        specialist(
            i,
            f"specialist-{i}",
            domains=["service"],
            trigger_hints=["service failed"],
            priority=i,
        )
        for i in range(1, 7)
    ]

    decision = make_router(
        *items,
        candidate_limit=12,
        selection_limit=4,
    ).route(
        report=report(),
        analysis=analysis(
            health_status="critical",
            issues=[issue("Service failed", severity="critical")],
        ),
    )

    assert len(decision.candidate_specialists) == 6
    assert len(decision.selected_specialists) == 4
    assert decision.candidate_slugs == tuple(
        f"specialist-{i}" for i in range(1, 7)
    )
    assert decision.selected_slugs == tuple(
        f"specialist-{i}" for i in range(1, 5)
    )


def test_candidate_limit_is_independent_from_selection_limit():
    items = [
        specialist(
            i,
            f"specialist-{i}",
            domains=["service"],
            trigger_hints=["service failed"],
            priority=i,
        )
        for i in range(1, 16)
    ]

    decision = make_router(
        *items,
        candidate_limit=12,
        selection_limit=4,
    ).route(
        report=report(),
        analysis=analysis(
            health_status="critical",
            issues=[issue("Service failed", severity="critical")],
        ),
    )

    assert len(decision.candidate_specialists) == 12
    assert len(decision.selected_specialists) == 4


def test_candidate_limit_must_be_at_least_selection_limit():
    with pytest.raises(
        ValueError,
        match="candidate_limit must be >= selection_limit",
    ):
        make_router(
            candidate_limit=3,
            selection_limit=4,
        )

def test_memory_issue_selects_memory_specialist():
    decision = make_router(*baseline()).route(
        report=report(),
        analysis=analysis(
            health_status="warning",
            issues=[
                issue(
                    "High memory usage",
                    description="High memory pressure with low available memory.",
                ),
            ],
        ),
    )
    assert decision.candidate_slugs == ("linux-memory",)
    assert decision.selected_slugs == ("linux-memory",)


def test_combined_cpu_memory_selects_both():
    decision = make_router(*baseline()).route(
        report=report(),
        analysis=analysis(
            health_status="critical",
            issues=[
                issue(
                    "High CPU utilization",
                    description="High cpu and cpu saturation.",
                ),
                issue(
                    "High memory usage",
                    description="High memory and low available memory.",
                ),
            ],
        ),
    )
    assert set(decision.candidate_slugs) == {"linux-cpu", "linux-memory"}
    assert set(decision.selected_slugs) == {"linux-cpu", "linux-memory"}


def test_domain_only_fallback_works_when_no_trigger_matches():
    custom = specialist(
        9,
        "database",
        domains=["database"],
        trigger_hints=["database connection failed"],
        priority=10,
    )
    decision = make_router(custom).route(
        report=report(),
        analysis=analysis(
            health_status="warning",
            issues=[
                issue(
                    "Database latency",
                    description="Database response is slow.",
                ),
            ],
        ),
    )
    assert decision.candidate_slugs == ("database",)
    assert decision.selected_slugs == ("database",)


def test_no_suitable_specialist_is_explicit():
    decision = make_router(*baseline()).route(
        report=report(),
        analysis=analysis(
            health_status="critical",
            issues=[
                issue(
                    "RAID controller firmware failure",
                    description=(
                        "Hardware controller reports an "
                        "unrecoverable firmware fault."
                    ),
                    severity="critical",
                ),
            ],
        ),
    )
    assert decision.should_investigate is True
    assert decision.candidate_specialists == ()
    assert decision.selected_specialists == ()
    assert RoutingReason.NO_SUITABLE_SPECIALIST in decision.reasons


def test_info_only_issue_is_not_actionable():
    decision = make_router(*baseline()).route(
        report=report(),
        analysis=analysis(
            health_status="healthy",
            issues=[
                issue(
                    "CPU information",
                    severity="info",
                    description="CPU utilization is normal.",
                ),
            ],
        ),
    )
    assert decision.should_investigate is False
    assert decision.candidate_specialists == ()
    assert decision.selected_specialists == ()
