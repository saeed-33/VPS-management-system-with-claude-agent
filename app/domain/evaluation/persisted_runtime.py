from __future__ import annotations

from dataclasses import dataclass

from app.domain.evaluation.contracts import (
    EvaluationMetric,
    EvaluationObservation,
)
from app.shared.dto.investigation_read_models import (
    InvestigationDetailReadModel,
)


@dataclass(slots=True, frozen=True)
class PersistedRuntimeEvaluation:
    investigation_id: str
    observations: tuple[
        EvaluationObservation,
        ...
    ]


class PersistedRuntimeEvaluator:
    """
    Evaluate persisted runtime snapshots without re-running
    Specialists, SSH, tools, or the LLM.

    This evaluator only emits metrics that can be proven from
    persisted Investigation state.
    """

    def evaluate(
        self,
        investigation: InvestigationDetailReadModel,
    ) -> PersistedRuntimeEvaluation:
        if not investigation.runtime_available:
            return PersistedRuntimeEvaluation(
                investigation_id=(
                    investigation.investigation_id
                ),
                observations=(),
            )

        runtime = investigation.runtime

        if runtime is None:
            return PersistedRuntimeEvaluation(
                investigation_id=(
                    investigation.investigation_id
                ),
                observations=(),
            )

        observations = (
            self._specialist_completion(
                investigation
            ),
            self._evidence_grounding(
                investigation
            ),
            self._budget_compliance(
                investigation
            ),
            self._conflict_preservation(
                investigation
            ),
            self._final_diagnosis_grounding(
                investigation
            ),
        )

        return PersistedRuntimeEvaluation(
            investigation_id=(
                investigation.investigation_id
            ),
            observations=observations,
        )

    def _specialist_completion(
        self,
        investigation,
    ) -> EvaluationObservation:
        runtime = investigation.runtime
        assert runtime is not None

        runs = tuple(
            item
            for item in runtime.specialist_runs
            if isinstance(item, dict)
        )

        passed = bool(runs) and all(
            item.get("status")
            == "completed"
            for item in runs
        )

        return EvaluationObservation(
            case_id=(
                f"persisted:"
                f"{investigation.investigation_id}:"
                "specialist-completion"
            ),
            metric=(
                EvaluationMetric
                .SPECIALIST_COMPLETION
            ),
            passed=passed,
            score=(
                1.0
                if passed
                else 0.0
            ),
            details=(
                f"{sum(1 for item in runs if item.get('status') == 'completed')}"
                f"/{len(runs)} Specialist runs completed."
            ),
            metadata={
                "investigation_id": (
                    investigation.investigation_id
                ),
                "source": "persisted-runtime",
            },
        )

    def _evidence_grounding(
        self,
        investigation,
    ) -> EvaluationObservation:
        runtime = investigation.runtime
        assert runtime is not None

        evidence_ids = {
            item.get("evidence_id")
            for item in runtime.evidence
            if isinstance(item, dict)
            and item.get("evidence_id")
        }

        referenced = set()

        for run in runtime.specialist_runs:
            if isinstance(run, dict):
                referenced.update(
                    run.get(
                        "evidence_ids"
                    )
                    or ()
                )

        for claim in runtime.correlated_claims:
            if isinstance(claim, dict):
                referenced.update(
                    claim.get(
                        "evidence_ids"
                    )
                    or ()
                )

        for conflict in runtime.conflicts:
            if isinstance(conflict, dict):
                referenced.update(
                    conflict.get(
                        "evidence_ids"
                    )
                    or ()
                )

        final_diagnosis = (
            runtime.final_diagnosis
        )

        if isinstance(
            final_diagnosis,
            dict,
        ):
            referenced.update(
                final_diagnosis.get(
                    "evidence_ids"
                )
                or ()
            )

        missing = sorted(
            referenced - evidence_ids
        )

        passed = not missing

        return EvaluationObservation(
            case_id=(
                f"persisted:"
                f"{investigation.investigation_id}:"
                "evidence-grounding"
            ),
            metric=(
                EvaluationMetric
                .EVIDENCE_GROUNDING
            ),
            passed=passed,
            score=(
                1.0
                if passed
                else 0.0
            ),
            details=(
                "All referenced Evidence IDs "
                "are persisted."
                if passed
                else (
                    "Missing Evidence IDs: "
                    + ", ".join(missing)
                )
            ),
            metadata={
                "investigation_id": (
                    investigation.investigation_id
                ),
                "referenced_evidence_count": (
                    len(referenced)
                ),
                "persisted_evidence_count": (
                    len(evidence_ids)
                ),
                "source": "persisted-runtime",
            },
        )

    def _budget_compliance(
        self,
        investigation,
    ) -> EvaluationObservation:
        runtime = investigation.runtime
        assert runtime is not None

        actions_used = (
            runtime.actions_used
            if runtime.actions_used is not None
            else 0
        )

        max_actions = (
            investigation.max_actions
        )

        passed = (
            actions_used <= max_actions
        )

        return EvaluationObservation(
            case_id=(
                f"persisted:"
                f"{investigation.investigation_id}:"
                "budget-compliance"
            ),
            metric=(
                EvaluationMetric
                .BUDGET_COMPLIANCE
            ),
            passed=passed,
            score=(
                1.0
                if passed
                else 0.0
            ),
            details=(
                f"{actions_used}/"
                f"{max_actions} actions used."
            ),
            metadata={
                "investigation_id": (
                    investigation.investigation_id
                ),
                "actions_used": actions_used,
                "max_actions": max_actions,
                "source": "persisted-runtime",
            },
        )

    def _conflict_preservation(
        self,
        investigation,
    ) -> EvaluationObservation:
        runtime = investigation.runtime
        assert runtime is not None

        conflicts = tuple(
            item
            for item in runtime.conflicts
            if isinstance(item, dict)
        )

        final_diagnosis = (
            runtime.final_diagnosis
        )

        narrative = runtime.narrative

        if not conflicts:
            passed = True
            details = (
                "No persisted conflict to preserve."
            )

        elif not isinstance(
            final_diagnosis,
            dict,
        ):
            passed = False
            details = (
                "Persisted conflicts exist but "
                "Final Diagnosis is missing."
            )

        else:
            persisted_conflict_ids = {
                item.get("conflict_id")
                for item in conflicts
                if item.get("conflict_id")
            }

            conflict_count = (
                final_diagnosis.get(
                    "conflict_count"
                )
            )

            narrative_ids = set()

            if isinstance(
                narrative,
                dict,
            ):
                narrative_ids.update(
                    narrative.get(
                        "conflict_ids"
                    )
                    or ()
                )

            count_preserved = (
                conflict_count
                == len(conflicts)
            )

            narrative_preserved = (
                not isinstance(
                    narrative,
                    dict,
                )
                or persisted_conflict_ids
                <= narrative_ids
            )

            passed = (
                count_preserved
                and narrative_preserved
            )

            details = (
                f"{len(conflicts)} persisted "
                "conflict(s); "
                f"diagnosis_count={conflict_count}; "
                f"narrative_refs="
                f"{len(narrative_ids)}."
            )

        return EvaluationObservation(
            case_id=(
                f"persisted:"
                f"{investigation.investigation_id}:"
                "conflict-preservation"
            ),
            metric=(
                EvaluationMetric
                .CONFLICT_PRESERVATION
            ),
            passed=passed,
            score=(
                1.0
                if passed
                else 0.0
            ),
            details=details,
            metadata={
                "investigation_id": (
                    investigation.investigation_id
                ),
                "conflict_count": (
                    len(conflicts)
                ),
                "source": "persisted-runtime",
            },
        )

    def _final_diagnosis_grounding(
        self,
        investigation,
    ) -> EvaluationObservation:
        runtime = investigation.runtime
        assert runtime is not None

        final_diagnosis = (
            runtime.final_diagnosis
        )

        narrative = runtime.narrative

        if not isinstance(
            final_diagnosis,
            dict,
        ):
            passed = False
            details = (
                "Final Diagnosis is missing."
            )

        else:
            persisted_claim_ids = {
                item.get("claim_id")
                for item
                in runtime.correlated_claims
                if isinstance(
                    item,
                    dict,
                )
                and item.get("claim_id")
            }

            persisted_conflict_ids = {
                item.get("conflict_id")
                for item
                in runtime.conflicts
                if isinstance(
                    item,
                    dict,
                )
                and item.get(
                    "conflict_id"
                )
            }

            if isinstance(
                narrative,
                dict,
            ):
                narrative_claim_ids = set(
                    narrative.get(
                        "claim_ids"
                    )
                    or ()
                )

                narrative_conflict_ids = set(
                    narrative.get(
                        "conflict_ids"
                    )
                    or ()
                )

                claims_valid = (
                    narrative_claim_ids
                    <= persisted_claim_ids
                )

                conflicts_valid = (
                    narrative_conflict_ids
                    <= persisted_conflict_ids
                )

            else:
                claims_valid = True
                conflicts_valid = True

            passed = (
                claims_valid
                and conflicts_valid
            )

            details = (
                "Narrative references only "
                "persisted Claim/Conflict IDs."
                if passed
                else (
                    "Narrative contains unknown "
                    "Claim/Conflict IDs."
                )
            )

        return EvaluationObservation(
            case_id=(
                f"persisted:"
                f"{investigation.investigation_id}:"
                "final-diagnosis-grounding"
            ),
            metric=(
                EvaluationMetric
                .FINAL_DIAGNOSIS_GROUNDING
            ),
            passed=passed,
            score=(
                1.0
                if passed
                else 0.0
            ),
            details=details,
            metadata={
                "investigation_id": (
                    investigation.investigation_id
                ),
                "source": "persisted-runtime",
            },
        )
