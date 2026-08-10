from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.investigation.contracts import InvestigationBudget
from app.agent.investigation.diagnostic_policy import (
    DiagnosticPolicyEngine,
    DiagnosticPolicyRequest,
)
from app.agent.investigation.diagnostic_tools import (
    DiagnosticToolCall,
    build_default_diagnostic_tool_registry,
)
from app.bootstrap import container


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("specialist")
    parser.add_argument("tool_id")
    parser.add_argument(
        "--arguments-json",
        default="{}",
    )
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
    args = parser.parse_args()

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

    result = DiagnosticPolicyEngine(
        registry=build_default_diagnostic_tool_registry()
    ).evaluate(
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
            investigation_budget=InvestigationBudget(
                max_specialists=4,
                max_rounds=args.investigation_max_rounds,
                max_actions=args.investigation_max_actions,
            ),
        ),
    )

    print()
    print("# Diagnostic Policy Decision")
    print()
    print(f"Specialist:             {result.specialist_slug}")
    print(f"Tool:                   {result.tool_id}")
    print(f"Decision:               {result.decision.value.upper()}")
    print(
        "Reasons:                "
        + ", ".join(
            reason.value
            for reason in result.reasons
        )
    )
    print(f"Round:                  {args.round}")
    print(
        "Specialist actions used:"
        f" {args.specialist_actions_used}"
        f"/{specialist.max_actions}"
    )
    print(
        "Investigation actions:  "
        f"{args.investigation_actions_used}"
        f"/{args.investigation_max_actions}"
    )

    if result.allowed:
        print()
        print("## APPROVED EXECUTION ENVELOPE")
        print()
        print(f"Command:      {result.rendered_command}")
        print(f"Timeout:      {result.timeout_seconds}s")
        print(f"Output limit: {result.output_limit_chars}")

    if "validation_error" in result.metadata:
        print()
        print(
            "Validation error: "
            + result.metadata["validation_error"]
        )

    print()
    print("SSH executed: NO")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
