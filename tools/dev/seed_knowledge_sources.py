from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.composition import container
from app.core.contracts.knowledge_sources import (
    CreateKnowledgeSourceDTO,
    UpdateKnowledgeSourceDTO,
)


@dataclass(frozen=True, slots=True)
class SeedKnowledgeSource:
    slug: str
    name: str
    description: str
    source_uri: str
    domains: tuple[str, ...]
    specialist_slugs: tuple[str, ...]
    tags: tuple[str, ...]
    priority: int = 20


SOURCES: tuple[SeedKnowledgeSource, ...] = (
    SeedKnowledgeSource(
        slug="linux-kernel-admin-guide",
        name="Linux Kernel Administration Guide",
        description=(
            "Official Linux kernel administration documentation "
            "for CPU, scheduler, memory, runtime and system behavior."
        ),
        source_uri="https://docs.kernel.org/admin-guide/index.html",
        domains=(
            "cpu",
            "scheduler",
            "memory",
            "process",
            "performance",
            "runtime",
        ),
        specialist_slugs=(
            "linux-cpu",
            "linux-memory",
            "linux-process",
        ),
        tags=(
            "official",
            "linux",
            "kernel",
        ),
        priority=10,
    ),
    SeedKnowledgeSource(
        slug="linux-proc-filesystem",
        name="Linux proc Filesystem Documentation",
        description=(
            "Official Linux kernel proc filesystem documentation "
            "for process and runtime inspection."
        ),
        source_uri="https://docs.kernel.org/filesystems/proc.html",
        domains=(
            "process",
            "runtime",
            "memory",
            "cpu",
        ),
        specialist_slugs=(
            "linux-process",
            "linux-cpu",
            "linux-memory",
        ),
        tags=(
            "official",
            "linux",
            "proc",
        ),
        priority=15,
    ),
    SeedKnowledgeSource(
        slug="linux-networking-docs",
        name="Linux Kernel Networking Documentation",
        description=(
            "Official Linux kernel networking documentation for "
            "network stack, sockets and connectivity diagnostics."
        ),
        source_uri="https://docs.kernel.org/networking/index.html",
        domains=(
            "network",
            "socket",
            "connectivity",
            "routing",
        ),
        specialist_slugs=(
            "linux-network",
        ),
        tags=(
            "official",
            "linux",
            "network",
        ),
        priority=10,
    ),
    SeedKnowledgeSource(
        slug="linux-filesystems-docs",
        name="Linux Kernel Filesystems Documentation",
        description=(
            "Official Linux kernel filesystem documentation for "
            "filesystem, storage and inode investigation."
        ),
        source_uri="https://docs.kernel.org/filesystems/index.html",
        domains=(
            "filesystem",
            "storage",
            "inode",
            "io",
            "disk",
        ),
        specialist_slugs=(
            "linux-storage",
        ),
        tags=(
            "official",
            "linux",
            "filesystem",
            "storage",
        ),
        priority=10,
    ),
    SeedKnowledgeSource(
        slug="systemd-man-pages",
        name="systemd Manual Pages",
        description=(
            "Official systemd manuals for services, units, journal "
            "and service-manager diagnostics."
        ),
        source_uri="https://www.freedesktop.org/software/systemd/man/latest/",
        domains=(
            "systemd",
            "service",
            "journal",
            "process",
        ),
        specialist_slugs=(
            "systemd-service",
        ),
        tags=(
            "official",
            "systemd",
            "service",
        ),
        priority=10,
    ),
    SeedKnowledgeSource(
        slug="docker-engine-docs",
        name="Docker Engine Documentation",
        description=(
            "Official Docker Engine documentation for containers, "
            "runtime, networking and performance."
        ),
        source_uri="https://docs.docker.com/engine/",
        domains=(
            "docker",
            "container",
            "runtime",
            "network",
            "performance",
        ),
        specialist_slugs=(
            "docker",
        ),
        tags=(
            "official",
            "docker",
            "container",
        ),
        priority=10,
    ),
    SeedKnowledgeSource(
        slug="nginx-docs",
        name="NGINX Documentation",
        description=(
            "Official NGINX documentation for HTTP, proxy, TLS "
            "and web-server diagnostics."
        ),
        source_uri="https://nginx.org/en/docs/",
        domains=(
            "nginx",
            "web_server",
            "http",
            "tls",
            "proxy",
        ),
        specialist_slugs=(
            "nginx",
        ),
        tags=(
            "official",
            "nginx",
            "http",
        ),
        priority=10,
    ),
    SeedKnowledgeSource(
        slug="postgresql-current-docs",
        name="PostgreSQL Current Documentation",
        description=(
            "Official PostgreSQL documentation for SQL, database "
            "operations, configuration and performance."
        ),
        source_uri="https://www.postgresql.org/docs/current/",
        domains=(
            "postgresql",
            "database",
            "sql",
            "performance",
        ),
        specialist_slugs=(
            "postgresql",
        ),
        tags=(
            "official",
            "postgresql",
            "database",
        ),
        priority=10,
    ),
)


def create_dto(
    item: SeedKnowledgeSource,
) -> CreateKnowledgeSourceDTO:
    return CreateKnowledgeSourceDTO(
        slug=item.slug,
        name=item.name,
        description=item.description,
        source_type="url",
        source_uri=item.source_uri,
        enabled=True,
        domains=item.domains,
        specialist_slugs=item.specialist_slugs,
        tags=item.tags,
        priority=item.priority,
        metadata={
            "seed": "phase-4.7.1",
            "authority": "official",
        },
    )


def update_dto(
    item: SeedKnowledgeSource,
) -> UpdateKnowledgeSourceDTO:
    return UpdateKnowledgeSourceDTO(
        name=item.name,
        description=item.description,
        source_type="url",
        source_uri=item.source_uri,
        enabled=True,
        domains=item.domains,
        specialist_slugs=item.specialist_slugs,
        tags=item.tags,
        priority=item.priority,
        metadata={
            "seed": "phase-4.7.1",
            "authority": "official",
        },
    )


def main() -> int:
    repository = (
        container
        .knowledge_source_repository
    )

    created = 0
    updated = 0

    for item in SOURCES:
        existing = repository.get_by_slug(
            item.slug
        )

        if existing is None:
            repository.create(
                create_dto(item)
            )
            created += 1
            print(
                f"Created: {item.slug}"
            )
            continue

        repository.update(
            existing.id,
            update_dto(item),
        )
        updated += 1
        print(
            f"Updated: {item.slug}"
        )

    snapshot = (
        container
        .knowledge_source_registry
        .snapshot()
    )

    print()
    print("Knowledge source seed complete")
    print("=" * 72)
    print(f"Created:         {created}")
    print(f"Updated:         {updated}")
    print(
        f"Enabled sources: {len(snapshot.sources)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
