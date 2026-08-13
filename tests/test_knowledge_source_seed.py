from tools.dev.seed_knowledge_sources import (
    SOURCES,
)


EXPECTED_SPECIALISTS = {
    "nginx",
    "postgresql",
    "docker",
    "linux-cpu",
    "linux-memory",
    "systemd-service",
    "linux-network",
    "linux-storage",
    "linux-process",
}


def test_seed_slugs_are_unique():
    slugs = [
        item.slug
        for item in SOURCES
    ]

    assert len(slugs) == len(set(slugs))


def test_seed_sources_are_official_https_urls():
    for item in SOURCES:
        assert item.source_uri.startswith(
            "https://"
        )
        assert "official" in item.tags


def test_seed_covers_all_baseline_specialists():
    covered = {
        slug
        for item in SOURCES
        for slug in item.specialist_slugs
    }

    assert EXPECTED_SPECIALISTS <= covered


def test_each_seed_has_routing_scope():
    for item in SOURCES:
        assert item.domains
        assert item.specialist_slugs
