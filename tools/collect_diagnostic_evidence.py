from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.domain.investigation.contracts import InvestigationBudget
from app.domain.investigation.diagnostic_policy import DiagnosticPolicyRequest
from app.domain.investigation.diagnostic_tools import DiagnosticToolCall
from app.domain.investigation.evidence_collection import (
    EvidenceCollectionRequest,
)
from app.bootstrap import container


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("server_id", type=int)
    parser.add_argument("specialist")
    parser.add_argument("tool_id")
    parser.add_argument("--arguments-json", default="{}")
    parser.add_argument("--evidence-id")
    parser.add_argument("--round", type=int, default=1)
    parser.add_argument(
        "--specialist-actions-used",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--investigation-actions-used",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--investigation-max-rounds",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--investigation-max-actions",
        type=int,
        default=12,
    )
    return parser.parse_args()


async def run(args) -> int:
    specialist = (
        container.specialist_registry.get_by_slug(
            args.specialist
        )
    )

    if specialist is None:
        raise SystemExit(
            f"Enabled Specialist not found: {args.specialist}"
        )

    try:
        arguments = json.loads(args.arguments_json)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Invalid --arguments-json: {exc}"
        ) from exc

    if not isinstance(arguments, dict):
        raise SystemExit(
            "--arguments-json must decode to an object."
        )

    policy_result = (
        container.diagnostic_policy_engine.evaluate(
            specialist=specialist,
            request=DiagnosticPolicyRequest(
                call=DiagnosticToolCall(
                    tool_id=args.tool_id,
                    arguments=arguments,
                ),
                round_number=args.round,
                specialist_actions_used=(
                    args.specialist_actions_used
                ),
                investigation_actions_used=(
                    args.investigation_actions_used
                ),
                investigation_budget=(
                    InvestigationBudget(
                        max_specialists=4,
                        max_rounds=(
                            args.investigation_max_rounds
                        ),
                        max_actions=(
                            args.investigation_max_actions
                        ),
                    )
                ),
            ),
        )
    )

    print()
    print("# Diagnostic Evidence Collection")
    print()
    print(f"Server ID:   {args.server_id}")
    print(f"Specialist:  {specialist.slug}")
    print(f"Tool:        {policy_result.tool_id}")
    print(
        f"Policy:      "
        f"{policy_result.decision.value.upper()}"
    )
    print(
        "Reasons:     "
        + ", ".join(
            item.value
            for item in policy_result.reasons
        )
    )

    if not policy_result.allowed:
        print()
        print("SSH executed: NO")
        return 2

    evidence_id = (
        args.evidence_id
        or (
            f"diagnostic:{args.server_id}:"
            f"{specialist.slug}:"
            f"{policy_result.tool_id}:"
            f"r{args.round}:"
            f"a{args.investigation_actions_used + 1}"
        )
    )

    evidence = await (
        container.evidence_collection_service.collect(
            EvidenceCollectionRequest(
                evidence_id=evidence_id,
                server_id=args.server_id,
                policy_result=policy_result,
            )
        )
    )

    print()
    print("## EVIDENCE")
    print()
    print(f"Evidence ID: {evidence.evidence_id}")
    print(f"Kind:        {evidence.kind.value}")
    print(
        f"Success:     "
        f"{evidence.metadata['success']}"
    )
    print(
        f"Exit status: "
        f"{evidence.metadata['exit_status']}"
    )
    print(
        f"Duration:    "
        f"{evidence.metadata['duration_ms']}ms"
    )
    print(
        f"Truncated:   "
        f"{evidence.metadata['excerpt_truncated']}"
    )
    print()
    print("## EXCERPT")
    print()
    print(evidence.excerpt)
    print()
    print("SSH executed: YES")

    return 0


def main() -> int:
    return asyncio.run(run(parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
