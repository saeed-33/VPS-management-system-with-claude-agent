from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str]) -> int:
    print()
    print(
        "$ " + " ".join(command)
    )
    completed = subprocess.run(
        command,
        cwd=ROOT,
    )
    return completed.returncode


def tool_exists(name: str) -> bool:
    return (
        ROOT
        / "tools"
        / name
    ).exists()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the documented chat_system "
            "test/evaluation sequence."
        )
    )
    parser.add_argument(
        "--mode",
        choices=(
            "quick",
            "full",
            "readiness",
        ),
        default="full",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
    )
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
    )
    args = parser.parse_args()

    commands = [
        [
            sys.executable,
            "-m",
            "pytest",
        ],
    ]

    if args.mode in {
        "full",
        "readiness",
    }:
        optional = (
            (
                "list_routes.py",
                [
                    sys.executable,
                    "tools/dev/list_routes.py",
                ],
            ),
            (
                "run_evaluation_dataset.py",
                [
                    sys.executable,
                    "tools/acceptance/run_evaluation_dataset.py",
                ],
            ),
            (
                "run_safety_runtime_evaluation.py",
                [
                    sys.executable,
                    "tools/acceptance/run_safety_runtime_evaluation.py",
                ],
            ),
        )

        for filename, command in optional:
            if tool_exists(filename):
                commands.append(command)

    if args.mode == "readiness":
        optional = (
            (
                "run_persisted_runtime_evaluation.py",
                [
                    sys.executable,
                    "tools/acceptance/run_persisted_runtime_evaluation.py",
                    "--limit",
                    str(args.limit),
                ],
            ),
            (
                "run_production_readiness_evaluation.py",
                [
                    sys.executable,
                    "tools/acceptance/run_production_readiness_evaluation.py",
                    "--limit",
                    str(args.limit),
                ],
            ),
        )

        for filename, command in optional:
            if tool_exists(filename):
                commands.append(command)

    failures = []

    for command in commands:
        code = run(command)

        if code != 0:
            failures.append(
                (
                    command,
                    code,
                )
            )

            if not args.continue_on_failure:
                break

    print()
    print(
        f"Commands executed: "
        f"{len(commands)}"
    )
    print(
        f"Failures: "
        f"{len(failures)}"
    )

    if failures:
        for command, code in failures:
            print(
                f"- {code}: "
                + " ".join(command)
            )

    return (
        0
        if not failures
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
