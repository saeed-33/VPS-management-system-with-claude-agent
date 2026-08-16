"""
أداة تطوير/تشخيص لتشغيل workflow أو فحص contracts والبيانات أثناء التطوير.

الموقع في المعمارية: Developer tooling.
يُستدعى بواسطة: CLI أو المطور مباشرة.
يعتمد مباشرة على: app.infrastructure.database.repositories.specialist_definition_repository، app.core.contracts.specialists.
الحد المعماري: ليست application boundary ولا ينبغي اعتبارها API production.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.infrastructure.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)
from app.core.contracts.specialists import (
    CreateSpecialistDefinitionDTO,
    UpdateSpecialistDefinitionDTO,
)


SPECIALISTS = [
    {
        "slug": "linux-cpu",
        "name": "Linux CPU Investigator",
        "description": (
            "Investigates abnormal Linux CPU utilization, "
            "load average, scheduler pressure, iowait, "
            "steal time and CPU-heavy processes."
        ),
        "instructions": (
            "Determine whether the observed symptoms represent "
            "real CPU saturation. Distinguish CPU utilization, "
            "load average, iowait, steal time and runnable-process "
            "pressure. Do not treat high load alone as proof of a "
            "CPU bottleneck. Prefer evidence tied to processes and "
            "system-wide CPU statistics."
        ),
        "domains": [
            "cpu",
            "process",
            "performance",
            "scheduler",
        ],
        "trigger_hints": [
            "high cpu",
            "cpu saturation",
            "high load average",
            "runaway process",
            "high iowait",
            "high steal time",
        ],
        "knowledge_topics": [
            "linux cpu",
            "load average",
            "process scheduling",
            "iowait",
            "steal time",
            "cpu saturation",
        ],
        "allowed_tool_ids": [
            "process-top-cpu",
            "vmstat-sample",
        ],
        "priority": 20,
        "max_rounds": 2,
        "max_actions": 4,
    },
    {
        "slug": "linux-memory",
        "name": "Linux Memory Investigator",
        "description": (
            "Investigates Linux memory pressure, swap activity, "
            "OOM events, memory growth and memory-heavy processes."
        ),
        "instructions": (
            "Distinguish used memory from actual memory pressure. "
            "Consider available memory, cache, swap, reclaim pressure "
            "and OOM events. Identify processes whose RSS or memory "
            "growth can explain the condition. Do not classify cache "
            "usage alone as a memory problem."
        ),
        "domains": [
            "memory",
            "swap",
            "oom",
            "process",
            "performance",
        ],
        "trigger_hints": [
            "high memory",
            "low available memory",
            "swap usage",
            "oom",
            "out of memory",
            "memory leak",
        ],
        "knowledge_topics": [
            "linux memory",
            "linux swap",
            "oom killer",
            "memory pressure",
            "process rss",
            "page cache",
        ],
        "allowed_tool_ids": [
            "process-top-memory",
            "memory-summary",
            "vmstat-sample",
        ],
        "priority": 20,
        "max_rounds": 2,
        "max_actions": 4,
    },
    {
        "slug": "linux-storage",
        "name": "Linux Storage & Filesystem Investigator",
        "description": (
            "Investigates disk capacity, filesystem exhaustion, "
            "inode pressure, storage latency and I/O bottlenecks."
        ),
        "instructions": (
            "Separate capacity problems from latency or throughput "
            "problems. Check filesystem usage, inode availability, "
            "mount health and I/O pressure. Identify the filesystem "
            "or workload responsible and avoid assuming that high "
            "disk utilization percentage always means low free space."
        ),
        "domains": [
            "disk",
            "filesystem",
            "storage",
            "io",
            "inode",
        ],
        "trigger_hints": [
            "disk full",
            "filesystem full",
            "high disk usage",
            "no space left",
            "inode exhaustion",
            "high io wait",
            "storage latency",
        ],
        "knowledge_topics": [
            "linux filesystem",
            "disk usage",
            "inode exhaustion",
            "linux block io",
            "storage latency",
        ],
        "allowed_tool_ids": [
            "disk-filesystems",
            "disk-path",
            "disk-inodes",
        ],
        "priority": 25,
        "max_rounds": 2,
        "max_actions": 4,
    },
    {
        "slug": "linux-network",
        "name": "Linux Network Investigator",
        "description": (
            "Investigates connectivity failures, listening ports, "
            "packet loss, routing, DNS and socket-level problems."
        ),
        "instructions": (
            "Determine whether the issue is local, remote, routing, "
            "DNS, firewall-related or application-port related. "
            "Correlate listening sockets and connection failures. "
            "Avoid concluding that a service is down solely because "
            "a remote connection failed."
        ),
        "domains": [
            "network",
            "dns",
            "routing",
            "socket",
            "connectivity",
        ],
        "trigger_hints": [
            "connection failed",
            "connection refused",
            "timeout",
            "dns failure",
            "packet loss",
            "port not listening",
            "network unreachable",
        ],
        "knowledge_topics": [
            "linux networking",
            "tcp",
            "dns",
            "routing",
            "socket troubleshooting",
            "connection timeout",
        ],
        "allowed_tool_ids": [
            "network-listeners",
            "network-sockets",
            "network-route",
            "network-connect",
        ],
        "priority": 25,
        "max_rounds": 2,
        "max_actions": 5,
    },
    {
        "slug": "systemd-service",
        "name": "Systemd Service Investigator",
        "description": (
            "Investigates failed, degraded or repeatedly restarting "
            "systemd services and their recent logs."
        ),
        "instructions": (
            "Verify the actual unit state before declaring a service "
            "failure. Correlate systemd status with recent journal "
            "evidence and dependency failures. Distinguish inactive "
            "by design from failed or crash-looping services."
        ),
        "domains": [
            "systemd",
            "service",
            "journal",
            "process",
        ],
        "trigger_hints": [
            "service failed",
            "unit failed",
            "service restarting",
            "systemctl failed",
            "journal error",
            "dependency failed",
        ],
        "knowledge_topics": [
            "systemd",
            "systemctl",
            "journalctl",
            "systemd dependencies",
            "service failure",
        ],
        "allowed_tool_ids": [
            "systemd-status",
            "systemd-failed",
            "journal-unit",
        ],
        "priority": 20,
        "max_rounds": 2,
        "max_actions": 4,
    },
    {
        "slug": "linux-process",
        "name": "Linux Process Investigator",
        "description": (
            "Investigates suspicious, blocked, runaway or resource-heavy "
            "Linux processes and process-level correlations."
        ),
        "instructions": (
            "Focus on process identity, state, resource usage, parent-child "
            "relationships and repeated abnormal behavior. Correlate the "
            "same PID or process name across CPU, memory and service evidence. "
            "Do not infer application-specific root causes without supporting "
            "evidence."
        ),
        "domains": [
            "process",
            "performance",
            "runtime",
        ],
        "trigger_hints": [
            "runaway process",
            "zombie process",
            "blocked process",
            "high cpu process",
            "high memory process",
            "process crash",
        ],
        "knowledge_topics": [
            "linux processes",
            "process states",
            "proc filesystem",
            "process resource usage",
        ],
        "allowed_tool_ids": [
            "process-top-cpu",
            "process-top-memory",
        ],
        "priority": 30,
        "max_rounds": 2,
        "max_actions": 4,
    },
    {
        "slug": "postgresql",
        "name": "PostgreSQL Investigator",
        "description": (
            "Investigates PostgreSQL availability, sessions, locks, "
            "slow queries, connection saturation and database resource usage."
        ),
        "instructions": (
            "Use PostgreSQL-specific evidence only when the server evidence "
            "indicates PostgreSQL is involved. Distinguish database symptoms "
            "from host-level CPU, memory or storage causes. Consider locks, "
            "long-running queries, connection pressure and database logs."
        ),
        "domains": [
            "postgresql",
            "database",
            "sql",
            "performance",
        ],
        "trigger_hints": [
            "postgres",
            "postgresql",
            "database connection",
            "too many connections",
            "slow query",
            "database lock",
            "deadlock",
        ],
        "knowledge_topics": [
            "postgresql",
            "postgresql performance",
            "postgresql locks",
            "postgresql connections",
            "postgresql logging",
        ],
        "allowed_tool_ids": [
            "postgres-ready",
        ],
        "priority": 15,
        "max_rounds": 3,
        "max_actions": 5,
    },
    {
        "slug": "nginx",
        "name": "Nginx Investigator",
        "description": (
            "Investigates Nginx availability, configuration, upstream, "
            "TLS and HTTP gateway problems."
        ),
        "instructions": (
            "Correlate Nginx service state, logs, listeners, upstream "
            "availability and HTTP status evidence. Distinguish Nginx "
            "configuration failures from upstream application failures. "
            "Use TLS evidence when certificate or handshake symptoms exist."
        ),
        "domains": [
            "nginx",
            "web_server",
            "http",
            "tls",
            "proxy",
        ],
        "trigger_hints": [
            "nginx",
            "502 bad gateway",
            "504 gateway timeout",
            "upstream failed",
            "tls error",
            "certificate error",
        ],
        "knowledge_topics": [
            "nginx",
            "nginx upstream",
            "nginx tls",
            "reverse proxy",
            "http gateway errors",
        ],
        "allowed_tool_ids": [
            "nginx-config-test",
            "nginx-version",
            "network-listeners",
            "systemd-status",
        ],
        "priority": 15,
        "max_rounds": 3,
        "max_actions": 5,
    },
    {
        "slug": "docker",
        "name": "Docker Investigator",
        "description": (
            "Investigates container lifecycle, resource pressure, "
            "health checks, networking and container log problems."
        ),
        "instructions": (
            "Identify the affected container and correlate container state "
            "with host-level resource evidence. Distinguish container failure "
            "from host resource exhaustion or external dependency failure. "
            "Do not assume a stopped container is abnormal unless evidence "
            "shows it should be running."
        ),
        "domains": [
            "docker",
            "container",
            "runtime",
            "network",
            "performance",
        ],
        "trigger_hints": [
            "container failed",
            "container exited",
            "unhealthy container",
            "docker error",
            "container restart",
            "container oom",
        ],
        "knowledge_topics": [
            "docker",
            "container health",
            "docker networking",
            "container resources",
            "docker logs",
        ],
        "allowed_tool_ids": [
            "docker-ps",
            "network-listeners",
        ],
        "priority": 20,
        "max_rounds": 3,
        "max_actions": 5,
    },
]


def build_create_dto(
    definition: dict,
) -> CreateSpecialistDefinitionDTO:
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى build_create_dto؛ المدخلات المهمة: definition.
    تعيد CreateSpecialistDefinitionDTO أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return CreateSpecialistDefinitionDTO(
        slug=definition["slug"],
        name=definition["name"],
        description=definition["description"],
        instructions=definition["instructions"],
        enabled=True,
        domains=definition["domains"],
        trigger_hints=definition["trigger_hints"],
        knowledge_topics=definition["knowledge_topics"],
        allowed_tool_ids=definition["allowed_tool_ids"],
        priority=definition["priority"],
        max_rounds=definition["max_rounds"],
        max_actions=definition["max_actions"],
        metadata={
            "seeded_by": "tools/dev/seed_specialists.py",
            "baseline": "phase-4",
        },
    )


def build_update_dto(
    definition: dict,
) -> UpdateSpecialistDefinitionDTO:
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى build_update_dto؛ المدخلات المهمة: definition.
    تعيد UpdateSpecialistDefinitionDTO أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return UpdateSpecialistDefinitionDTO(
        name=definition["name"],
        description=definition["description"],
        instructions=definition["instructions"],
        enabled=True,
        domains=definition["domains"],
        trigger_hints=definition["trigger_hints"],
        knowledge_topics=definition["knowledge_topics"],
        allowed_tool_ids=definition["allowed_tool_ids"],
        priority=definition["priority"],
        max_rounds=definition["max_rounds"],
        max_actions=definition["max_actions"],
        metadata={
            "seeded_by": "tools/dev/seed_specialists.py",
            "baseline": "phase-4",
        },
    )


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Create the baseline user-defined specialist "
            "definitions for Phase 4."
        )
    )

    parser.add_argument(
        "--update-existing",
        action="store_true",
        help=(
            "Update matching slugs instead of skipping them."
        ),
    )

    args = parser.parse_args()

    repository = SpecialistDefinitionRepository()

    created = 0
    updated = 0
    skipped = 0

    print()
    print("Seeding specialist definitions")
    print("=" * 72)

    for definition in SPECIALISTS:
        slug = definition["slug"]

        existing = repository.get_by_slug(
            slug
        )

        if existing is None:
            specialist = repository.create(
                build_create_dto(
                    definition
                )
            )

            created += 1

            print(
                f"[CREATED] #{specialist.id:<4} "
                f"{specialist.slug:<20} "
                f"{specialist.name}"
            )

            continue

        if not args.update_existing:
            skipped += 1

            print(
                f"[SKIPPED] #{existing.id:<4} "
                f"{existing.slug:<20} "
                f"{existing.name}"
            )

            continue

        specialist = repository.update(
            existing.id,
            build_update_dto(
                definition
            ),
        )

        updated += 1

        print(
            f"[UPDATED] #{specialist.id:<4} "
            f"{specialist.slug:<20} "
            f"{specialist.name}"
        )

    print()
    print("Summary")
    print("-" * 72)
    print(
        f"Created: {created}"
    )
    print(
        f"Updated: {updated}"
    )
    print(
        f"Skipped: {skipped}"
    )
    print(
        f"Total definitions: "
        f"{len(SPECIALISTS)}"
    )

    print()
    print(
        "Note: allowed_tool_ids reference the registered, "
        "read-only Diagnostic Tool Registry."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
