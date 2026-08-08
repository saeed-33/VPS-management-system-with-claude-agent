from types import SimpleNamespace

from app.agent.investigation.investigation_router import (
    InvestigationRouter,
    RoutingReason,
)
from app.agent.investigation.specialist_registry import (
    SpecialistRegistry,
)


def specialist(
    specialist_id: int,
    slug: str,
    *,
    domains: list[str],
    trigger_hints: list[str],
    priority: int = 100,
):
    return SimpleNamespace(
        id=specialist_id,
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
        return [
            item
            for item in self.items
            if item.enabled
        ]


def router(*items):
    return InvestigationRouter(
        specialist_registry=(
            SpecialistRegistry(
                FakeRepository(
                    list(items)
                )
            )
        )
    )


def report(
    *,
    status="success",
    connection_successful=True,
    commands_failed=0,
    error_message=None,
    executions=None,
):
    return SimpleNamespace(
        status=status,
        connection_successful=(
            connection_successful
        ),
        commands_failed=commands_failed,
        error_message=error_message,
        executions=executions or [],
    )


def analysis(
    *,
    health_status="healthy",
    issues=None,
    summary="",
):
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


def baseline_specialists():
    return (
        specialist(
            1,
            "linux-cpu",
            domains=[
                "cpu",
                "process",
                "performance",
            ],
            trigger_hints=[
                "high cpu",
                "cpu saturation",
                "high load average",
            ],
            priority=20,
        ),
        specialist(
            2,
            "linux-memory",
            domains=[
                "memory",
                "swap",
                "process",
                "performance",
            ],
            trigger_hints=[
                "high memory",
                "low available memory",
                "swap usage",
            ],
            priority=20,
        ),
        specialist(
            3,
            "linux-process",
            domains=[
                "process",
                "performance",
            ],
            trigger_hints=[
                "runaway process",
            ],
            priority=30,
        ),
    )


def test_healthy_report_does_not_open_investigation():
    decision = router(
        *baseline_specialists()
    ).route(
        report=report(),
        analysis=analysis(),
    )

    assert decision.should_investigate is False
    assert decision.selected_specialists == ()
    assert (
        RoutingReason.HEALTHY_NO_ISSUES
        in decision.reasons
    )


def test_cpu_issue_selects_cpu_specialist_only():
    decision = router(
        *baseline_specialists()
    ).route(
        report=report(),
        analysis=analysis(
            health_status="warning",
            issues=[
                issue(
                    "High CPU utilization",
                    description=(
                        "The server shows high cpu "
                        "usage and cpu saturation."
                    ),
                ),
            ],
        ),
    )

    assert decision.should_investigate is True
    assert decision.selected_slugs == (
        "linux-cpu",
    )
    assert "cpu" in decision.detected_domains


def test_memory_issue_selects_memory_specialist():
    decision = router(
        *baseline_specialists()
    ).route(
        report=report(),
        analysis=analysis(
            health_status="warning",
            issues=[
                issue(
                    "High memory usage",
                    description=(
                        "High memory pressure with "
                        "low available memory."
                    ),
                ),
            ],
        ),
    )

    assert decision.selected_slugs == (
        "linux-memory",
    )


def test_combined_cpu_memory_selects_both():
    decision = router(
        *baseline_specialists()
    ).route(
        report=report(),
        analysis=analysis(
            health_status="critical",
            issues=[
                issue(
                    "High CPU utilization",
                    description=(
                        "High cpu and cpu saturation."
                    ),
                ),
                issue(
                    "High memory usage",
                    description=(
                        "High memory and low "
                        "available memory."
                    ),
                ),
            ],
        ),
    )

    assert set(
        decision.selected_slugs
    ) == {
        "linux-cpu",
        "linux-memory",
    }

    assert (
        decision.unmatched_issue_indexes
        == ()
    )


def test_domain_only_fallback_works_when_no_trigger_matches():
    custom = specialist(
        9,
        "database",
        domains=["database"],
        trigger_hints=[
            "database connection failed",
        ],
        priority=10,
    )

    decision = router(
        custom
    ).route(
        report=report(),
        analysis=analysis(
            health_status="warning",
            issues=[
                issue(
                    "Database latency",
                    description=(
                        "Database response is slow."
                    ),
                ),
            ],
        ),
    )

    assert decision.selected_slugs == (
        "database",
    )


def test_no_suitable_specialist_is_explicit():
    decision = router(
        *baseline_specialists()
    ).route(
        report=report(),
        analysis=analysis(
            health_status="critical",
            issues=[
                issue(
                    "RAID controller firmware failure",
                    description=(
                        "Hardware controller reports "
                        "an unrecoverable firmware fault."
                    ),
                    severity="critical",
                ),
            ],
        ),
    )

    assert decision.should_investigate is True
    assert decision.selected_specialists == ()
    assert (
        RoutingReason.NO_SUITABLE_SPECIALIST
        in decision.reasons
    )
    assert decision.unmatched_issue_indexes == (
        0,
    )


def test_report_connection_failure_can_route_network_specialist():
    network = specialist(
        4,
        "linux-network",
        domains=["network", "connectivity"],
        trigger_hints=["connection failed", "network unreachable"],
        priority=20,
    )
    cpu = specialist(
        5,
        "linux-cpu",
        domains=["cpu", "process", "performance"],
        trigger_hints=["high cpu"],
        priority=20,
    )
    memory = specialist(
        6,
        "linux-memory",
        domains=["memory", "process", "performance"],
        trigger_hints=["high memory"],
        priority=20,
    )

    decision = router(network, cpu, memory).route(
        report=report(
            status="connection_failed",
            connection_successful=False,
            error_message=(
                "OSError: [Errno 10013] Connect call failed "
                "('192.168.127.142', 22)"
            ),
        ),
        analysis=analysis(
            health_status="critical",
            summary=(
                "The monitoring report indicates a critical failure "
                "in establishing connectivity to the target server. "
                "Immediate investigation into network path and SSH "
                "service status is required."
            ),
            issues=[
                issue(
                    "Connection Failure to Target Server",
                    severity="critical",
                    description=(
                        "The monitoring process failed entirely due "
                        "to an inability to connect to the server."
                    ),
                    evidence=(
                        "OSError: [Errno 10013] Connect call failed "
                        "('192.168.127.142', 22)"
                    ),
                ),
            ],
        ),
    )

    assert decision.should_investigate is True
    assert decision.selected_slugs == ("linux-network",)
    assert RoutingReason.REPORT_FAILURE in decision.reasons


def test_info_only_issue_is_not_actionable():
    decision = router(
        *baseline_specialists()
    ).route(
        report=report(),
        analysis=analysis(
            health_status="healthy",
            issues=[
                issue(
                    "CPU information",
                    severity="info",
                    description=(
                        "CPU utilization is normal."
                    ),
                ),
            ],
        ),
    )

    assert decision.should_investigate is False
    assert decision.selected_specialists == ()


def test_max_specialists_budget_is_enforced():
    specialists = [
        specialist(
            index,
            f"specialist-{index}",
            domains=["service"],
            trigger_hints=[
                "service failed",
            ],
            priority=index,
        )
        for index in range(
            1,
            7,
        )
    ]

    decision = InvestigationRouter(
        specialist_registry=(
            SpecialistRegistry(
                FakeRepository(
                    specialists
                )
            )
        ),
        max_specialists=4,
    ).route(
        report=report(),
        analysis=analysis(
            health_status="critical",
            issues=[
                issue(
                    "Service failed",
                    severity="critical",
                ),
            ],
        ),
    )

    assert len(
        decision.selected_specialists
    ) == 4

    assert decision.selected_slugs == (
        "specialist-1",
        "specialist-2",
        "specialist-3",
        "specialist-4",
    )
