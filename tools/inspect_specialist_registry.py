from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.capabilities.investigation.specialist_registry import SpecialistRegistry
from app.infrastructure.database.repositories.specialist_definition_repository import (
    SpecialistDefinitionRepository,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument("--domain")
    group.add_argument("--domains")
    parser.add_argument("--require-all", action="store_true")
    args = parser.parse_args()

    snapshot = SpecialistRegistry(
        SpecialistDefinitionRepository()
    ).snapshot()

    print()
    print("Specialist Registry Snapshot")
    print("=" * 88)
    print(f"Enabled definitions: {len(snapshot.definitions)}")

    if args.domain:
        items = snapshot.find_by_domain(args.domain)
        print(f"Domain: {args.domain}")
        print("-" * 88)
        for item in items:
            print(
                f"{item.slug:<24} priority={item.priority:<4} "
                f"domains={','.join(item.domains)}"
            )
        print(f"Matches: {len(items)}")
        return 0

    if args.domains:
        requested = [
            item.strip()
            for item in args.domains.split(",")
            if item.strip()
        ]
        matches = snapshot.find_by_domains(
            requested,
            require_all=args.require_all,
        )

        print("Requested domains: " + ", ".join(requested))
        print(f"Require all: {args.require_all}")
        print("-" * 88)

        for match in matches:
            item = match.specialist
            print(
                f"{item.slug:<24} matched={match.matched_count:<2} "
                f"coverage={match.coverage:.0%} "
                f"priority={item.priority:<4} "
                f"[{', '.join(match.matched_domains)}]"
            )

        print(f"Matches: {len(matches)}")
        return 0

    print()
    print(f"{'SLUG':24} {'PRIORITY':8} {'ROUNDS':6} {'ACTIONS':7} DOMAINS")
    print("-" * 88)

    for item in snapshot.definitions:
        print(
            f"{item.slug:24} {item.priority:<8} "
            f"{item.max_rounds:<6} {item.max_actions:<7} "
            f"{', '.join(item.domains)}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
