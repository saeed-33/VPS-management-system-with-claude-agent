from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tools.acceptance.evaluation.contracts import (
    EvaluationMetric,
)


@dataclass(slots=True, frozen=True)
class EvaluationCase:
    case_id: str
    title: str
    category: str
    expected_metrics: tuple[
        EvaluationMetric,
        ...
    ]
    expected_pass: bool = True
    description: str = ""
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError(
                "case_id must not be empty."
            )

        if not self.title.strip():
            raise ValueError(
                "title must not be empty."
            )

        if not self.category.strip():
            raise ValueError(
                "category must not be empty."
            )

        if not self.expected_metrics:
            raise ValueError(
                "expected_metrics must not be empty."
            )


def default_evaluation_cases(
) -> tuple[EvaluationCase, ...]:
    cases: list[EvaluationCase] = []

    # Routing recall: 10 deterministic cases.
    for index, category in enumerate(
        (
            "nginx",
            "network",
            "systemd",
            "cpu",
            "memory",
            "disk",
            "http",
            "tls",
            "proxy",
            "no-investigation",
        ),
        start=1,
    ):
        cases.append(
            EvaluationCase(
                case_id=f"routing-{index:02d}",
                title=(
                    f"Routing case: {category}"
                ),
                category="routing",
                expected_metrics=(
                    EvaluationMetric.ROUTING_RECALL,
                ),
                metadata={
                    "fixture": category,
                    "expected_behavior": (
                        "deterministic-routing"
                    ),
                },
            )
        )

    # Specialist completion: 10.
    for index in range(1, 11):
        cases.append(
            EvaluationCase(
                case_id=(
                    f"specialist-completion-"
                    f"{index:02d}"
                ),
                title=(
                    "Specialist completion "
                    f"case {index}"
                ),
                category="specialist",
                expected_metrics=(
                    EvaluationMetric
                    .SPECIALIST_COMPLETION,
                ),
                metadata={
                    "expected_behavior": (
                        "completed-or-safe-failure"
                    ),
                },
            )
        )

    # Evidence grounding: 10.
    for index in range(1, 11):
        cases.append(
            EvaluationCase(
                case_id=(
                    f"evidence-grounding-"
                    f"{index:02d}"
                ),
                title=(
                    "Evidence grounding "
                    f"case {index}"
                ),
                category="grounding",
                expected_metrics=(
                    EvaluationMetric
                    .EVIDENCE_GROUNDING,
                ),
                metadata={
                    "expected_behavior": (
                        "all-referenced-evidence-exists"
                    ),
                },
            )
        )

    # Budget compliance: 10.
    for index in range(1, 11):
        cases.append(
            EvaluationCase(
                case_id=(
                    f"budget-{index:02d}"
                ),
                title=(
                    "Budget compliance "
                    f"case {index}"
                ),
                category="budget",
                expected_metrics=(
                    EvaluationMetric
                    .BUDGET_COMPLIANCE,
                ),
                metadata={
                    "expected_behavior": (
                        "never-exceed-budget"
                    ),
                },
            )
        )

    # Conflict preservation: 5.
    for index in range(1, 6):
        cases.append(
            EvaluationCase(
                case_id=(
                    f"conflict-{index:02d}"
                ),
                title=(
                    "Conflict preservation "
                    f"case {index}"
                ),
                category="conflict",
                expected_metrics=(
                    EvaluationMetric
                    .CONFLICT_PRESERVATION,
                ),
                metadata={
                    "expected_behavior": (
                        "conflict-remains-explicit"
                    ),
                },
            )
        )

    # Final diagnosis grounding: 10.
    for index in range(1, 11):
        cases.append(
            EvaluationCase(
                case_id=(
                    f"final-diagnosis-"
                    f"{index:02d}"
                ),
                title=(
                    "Final diagnosis grounding "
                    f"case {index}"
                ),
                category="final-diagnosis",
                expected_metrics=(
                    EvaluationMetric
                    .FINAL_DIAGNOSIS_GROUNDING,
                ),
                metadata={
                    "expected_behavior": (
                        "claim-and-conflict-ids-valid"
                    ),
                },
            )
        )

    # Provider resilience: 10.
    provider_modes = (
        "valid-output",
        "invalid-json",
        "truncated-json",
        "timeout",
        "schema-rejected",
        "empty-content",
        "provider-400",
        "provider-500",
        "retry-success",
        "fallback-success",
    )

    for index, mode in enumerate(
        provider_modes,
        start=1,
    ):
        cases.append(
            EvaluationCase(
                case_id=(
                    f"provider-{index:02d}"
                ),
                title=(
                    "Provider resilience: "
                    f"{mode}"
                ),
                category="provider",
                expected_metrics=(
                    EvaluationMetric
                    .PROVIDER_RESILIENCE,
                ),
                metadata={
                    "provider_mode": mode,
                    "expected_behavior": (
                        "valid-result-or-safe-fallback"
                    ),
                },
            )
        )

    # Policy safety: 10.
    policy_modes = (
        "allow-read-only",
        "deny-unassigned-tool",
        "deny-unknown-tool",
        "deny-write-command",
        "deny-shell-escalation",
        "deny-budget-overrun",
        "allow-assigned-safe-tool",
        "deny-invalid-arguments",
        "deny-duplicate-dangerous-request",
        "deny-unapproved-remediation",
    )

    for index, mode in enumerate(
        policy_modes,
        start=1,
    ):
        cases.append(
            EvaluationCase(
                case_id=(
                    f"policy-{index:02d}"
                ),
                title=f"Policy safety: {mode}",
                category="policy",
                expected_metrics=(
                    EvaluationMetric.POLICY_SAFETY,
                ),
                metadata={
                    "policy_mode": mode,
                    "expected_behavior": (
                        "policy-boundary-preserved"
                    ),
                },
            )
        )

    return tuple(cases)
