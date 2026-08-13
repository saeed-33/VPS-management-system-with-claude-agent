from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.composition import container


EXPECTED_SPECIALISTS = (
    "nginx",
    "postgresql",
    "docker",
    "linux-cpu",
    "linux-memory",
    "systemd-service",
    "linux-network",
    "linux-storage",
    "linux-process",
)


def main() -> int:
    snapshot = (
        container
        .knowledge_source_registry
        .snapshot()
    )

    failures: list[str] = []

    print()
    print("Knowledge Source Acceptance")
    print("=" * 88)

    for specialist_slug in EXPECTED_SPECIALISTS:
        sources = (
            snapshot
            .find_for_specialist(
                specialist_slug
            )
        )

        print(
            f"{specialist_slug:20} "
            f"sources={len(sources):2}  "
            + ", ".join(
                item.slug
                for item in sources
            )
        )

        if not sources:
            failures.append(
                specialist_slug
            )

    print()
    print(
        f"Enabled sources: {len(snapshot.sources)}"
    )
    print(
        f"Covered specialists: "
        f"{len(EXPECTED_SPECIALISTS) - len(failures)}"
        f"/{len(EXPECTED_SPECIALISTS)}"
    )

    if failures:
        print()
        print(
            "FAILED: no knowledge source for "
            + ", ".join(failures)
        )
        return 1

    print()
    print(
        "Knowledge source acceptance: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
