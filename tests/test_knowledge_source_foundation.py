from types import SimpleNamespace

import pytest

from app.capabilities.knowledge.source_registry import (
    KnowledgeSourceRegistry,
)
from app.core.contracts.knowledge_sources import (
    CreateKnowledgeSourceDTO,
)


class FakeRepository:
    def __init__(self, items=None):
        self.items = list(
            items or []
        )

    def list_enabled(self):
        return [
            item
            for item in self.items
            if item.enabled
        ]


def source(
    source_id,
    slug,
    *,
    domains=(),
    specialist_slugs=(),
    enabled=True,
    priority=100,
):
    return SimpleNamespace(
        id=source_id,
        slug=slug,
        name=slug,
        description=None,
        source_type="url",
        source_uri=(
            "https://example.com/"
            + slug
        ),
        inline_content=None,
        enabled=enabled,
        domains=list(domains),
        specialist_slugs=list(
            specialist_slugs
        ),
        tags=[],
        priority=priority,
        source_metadata={},
    )


def test_url_source_requires_uri():
    with pytest.raises(
        ValueError,
        match="requires source_uri",
    ):
        CreateKnowledgeSourceDTO(
            slug="linux-docs",
            name="Linux docs",
            source_type="url",
        )


def test_inline_source_requires_content():
    with pytest.raises(
        ValueError,
        match="requires inline_content",
    ):
        CreateKnowledgeSourceDTO(
            slug="internal-runbook",
            name="Internal Runbook",
            source_type="inline",
        )


def test_create_dto_normalizes_scope():
    dto = CreateKnowledgeSourceDTO(
        slug="Linux-CPU-Docs",
        name=" Linux CPU Docs ",
        source_type="URL",
        source_uri=" https://example.com/cpu ",
        domains=(
            " CPU ",
            "cpu",
            "Performance",
        ),
        specialist_slugs=(
            "linux-cpu",
            "LINUX-CPU",
        ),
    )

    assert dto.slug == "linux-cpu-docs"
    assert dto.name == "Linux CPU Docs"
    assert dto.source_type == "url"
    assert dto.domains == (
        "cpu",
        "performance",
    )
    assert dto.specialist_slugs == (
        "linux-cpu",
    )


def test_registry_excludes_disabled_sources():
    registry = KnowledgeSourceRegistry(
        FakeRepository(
            [
                source(
                    1,
                    "enabled",
                    enabled=True,
                ),
                source(
                    2,
                    "disabled",
                    enabled=False,
                ),
            ]
        )
    )

    assert [
        item.slug
        for item
        in registry.snapshot().sources
    ] == ["enabled"]


def test_registry_finds_sources_by_domain():
    registry = KnowledgeSourceRegistry(
        FakeRepository(
            [
                source(
                    1,
                    "cpu-guide",
                    domains=("cpu",),
                    priority=20,
                ),
                source(
                    2,
                    "network-guide",
                    domains=("network",),
                    priority=10,
                ),
            ]
        )
    )

    assert [
        item.slug
        for item in (
            registry.snapshot()
            .find_by_domain("CPU")
        )
    ] == ["cpu-guide"]


def test_registry_finds_sources_for_specialist():
    registry = KnowledgeSourceRegistry(
        FakeRepository(
            [
                source(
                    1,
                    "cpu-guide",
                    specialist_slugs=(
                        "linux-cpu",
                    ),
                ),
                source(
                    2,
                    "generic-guide",
                ),
            ]
        )
    )

    assert [
        item.slug
        for item in (
            registry.snapshot()
            .find_for_specialist(
                "LINUX-CPU"
            )
        )
    ] == ["cpu-guide"]
