from types import SimpleNamespace

import pytest

from app.domain.investigation.specialist_registry import (
    SpecialistRegistry,
    SpecialistRegistryValidationError,
)


def specialist(
    specialist_id: int,
    slug: str,
    *,
    enabled: bool = True,
    priority: int = 100,
    domains: list[str] | None = None,
    name: str | None = None,
):
    return SimpleNamespace(
        id=specialist_id,
        slug=slug,
        name=name or slug,
        description=None,
        instructions=None,
        enabled=enabled,
        domains=domains or [],
        trigger_hints=[],
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
        self.calls = 0

    def list_enabled(self):
        self.calls += 1
        return [item for item in self.items if item.enabled]


def test_disabled_specialists_are_excluded():
    registry = SpecialistRegistry(
        FakeRepository([
            specialist(1, "cpu", domains=["cpu"]),
            specialist(2, "memory", enabled=False, domains=["memory"]),
        ])
    )

    assert [item.slug for item in registry.get_enabled()] == ["cpu"]


def test_snapshot_is_stable_and_uses_one_repository_read():
    cpu = specialist(1, "cpu", domains=["cpu"])
    repository = FakeRepository([cpu])
    registry = SpecialistRegistry(repository)

    snapshot = registry.snapshot()
    assert repository.calls == 1
    assert snapshot.get_by_slug("cpu") is not None

    cpu.enabled = False
    assert snapshot.get_by_slug("cpu") is not None
    assert registry.snapshot().get_by_slug("cpu") is None
    assert repository.calls == 2


def test_registry_order_is_deterministic():
    registry = SpecialistRegistry(
        FakeRepository([
            specialist(3, "zeta", priority=50, domains=["cpu"], name="Zeta"),
            specialist(2, "alpha", priority=20, domains=["cpu"], name="Alpha"),
            specialist(1, "beta", priority=20, domains=["cpu"], name="Beta"),
        ])
    )

    assert [item.slug for item in registry.get_enabled()] == [
        "alpha",
        "beta",
        "zeta",
    ]


def test_domain_lookup_is_case_insensitive():
    registry = SpecialistRegistry(
        FakeRepository([
            specialist(1, "cpu", domains=[" CPU ", "Process"]),
        ])
    )

    assert [item.slug for item in registry.find_by_domain(" cpu ")] == ["cpu"]
    assert [item.slug for item in registry.find_by_domain("PROCESS")] == ["cpu"]


def test_multi_domain_lookup_prefers_more_matches():
    registry = SpecialistRegistry(
        FakeRepository([
            specialist(1, "cpu", priority=20, domains=["cpu", "performance"]),
            specialist(2, "process", priority=10, domains=["cpu", "process", "performance"]),
            specialist(3, "memory", priority=1, domains=["memory"]),
        ])
    )

    matches = registry.find_by_domains(["cpu", "process"])

    assert [match.specialist.slug for match in matches] == ["process", "cpu"]
    assert matches[0].matched_domains == ("cpu", "process")
    assert matches[0].coverage == 1.0


def test_require_all_filters_partial_matches():
    registry = SpecialistRegistry(
        FakeRepository([
            specialist(1, "cpu", domains=["cpu"]),
            specialist(2, "process", domains=["cpu", "process"]),
        ])
    )

    matches = registry.find_by_domains(
        ["cpu", "process"],
        require_all=True,
    )

    assert [match.specialist.slug for match in matches] == ["process"]


def test_invalid_definition_fails_snapshot():
    invalid = specialist(1, "cpu", domains=["cpu"])
    invalid.max_rounds = 0

    registry = SpecialistRegistry(FakeRepository([invalid]))

    with pytest.raises(
        SpecialistRegistryValidationError,
        match="max_rounds",
    ):
        registry.snapshot()


def test_invalid_domains_payload_fails_snapshot():
    invalid = specialist(1, "cpu", domains=["cpu"])
    invalid.domains = "cpu"

    registry = SpecialistRegistry(FakeRepository([invalid]))

    with pytest.raises(
        SpecialistRegistryValidationError,
        match="domains must be a JSON list",
    ):
        registry.snapshot()


def test_duplicate_domains_are_normalized():
    registry = SpecialistRegistry(
        FakeRepository([
            specialist(
                1,
                "cpu",
                domains=["CPU", " cpu ", "Process"],
            ),
        ])
    )

    item = registry.get_by_slug("cpu")

    assert item is not None
    assert item.domains == ("cpu", "process")
