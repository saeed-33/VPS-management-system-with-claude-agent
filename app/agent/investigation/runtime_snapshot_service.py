from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.agent.investigation.correlation import FinalDiagnosis
from app.agent.investigation.final_diagnosis_synthesizer import (
    FinalDiagnosisNarrative,
)
from app.agent.investigation.server_coordinator import (
    ServerCoordinatorResult,
)
from app.shared.database.repositories.investigation_repository import (
    InvestigationRepository,
)


class InvestigationRuntimeSnapshotService:
    """
    Persist a bounded operator-facing snapshot of accepted runtime state.

    The snapshot is intentionally a read projection, not a second
    orchestration state store. LangGraph/runtime objects are converted
    into JSON-safe primitives before persistence.
    """

    SNAPSHOT_VERSION = "4.19.2-v1"

    def __init__(
        self,
        repository: InvestigationRepository,
    ) -> None:
        self._repository = repository

    def persist(
        self,
        *,
        investigation_id: str,
        coordinator_result: ServerCoordinatorResult,
        final_diagnosis: FinalDiagnosis | None = None,
        narrative: FinalDiagnosisNarrative | None = None,
    ):
        if not investigation_id.strip():
            raise ValueError(
                "investigation_id must not be empty."
            )

        model = self._repository.get_by_investigation_id(
            investigation_id
        )

        if model is None:
            raise ValueError(
                "Investigation not found: "
                f"{investigation_id}"
            )

        runtime_id = (
            coordinator_result
            .state
            .investigation_id
        )

        metadata = dict(
            model.investigation_metadata
            or {}
        )

        snapshot = self.build_snapshot(
            coordinator_result=coordinator_result,
            final_diagnosis=final_diagnosis,
            narrative=narrative,
        )

        metadata["runtime_snapshot"] = snapshot
        metadata["runtime_snapshot_version"] = (
            self.SNAPSHOT_VERSION
        )
        metadata[
            "runtime_investigation_id"
        ] = runtime_id

        return self._repository.update_runtime_snapshot(
            investigation_id=investigation_id,
            status=(
                coordinator_result
                .state
                .status
                .value
            ),
            metadata=metadata,
        )

    def build_snapshot(
        self,
        *,
        coordinator_result: ServerCoordinatorResult,
        final_diagnosis: FinalDiagnosis | None = None,
        narrative: FinalDiagnosisNarrative | None = None,
    ) -> dict:
        state = coordinator_result.state

        specialist_runs = tuple(
            self._serialize_run(run)
            for run in coordinator_result.runs
        )

        evidence = tuple(
            self._serialize_evidence(item)
            for item in state.evidence
        )

        snapshot = {
            "version": self.SNAPSHOT_VERSION,
            "status": state.status.value,
            "orchestrator": (
                state.metadata.get(
                    "orchestrator"
                )
            ),
            "execution_mode": (
                state.metadata.get(
                    "execution_mode"
                )
            ),
            "waves_completed": (
                state.metadata.get(
                    "waves_completed"
                )
            ),
            "actions_used": (
                coordinator_result
                .investigation_actions_used
            ),
            "evidence_count": len(evidence),
            "specialist_runs": list(
                specialist_runs
            ),
            "evidence": list(evidence),
            "correlated_claims": [],
            "conflicts": [],
            "final_diagnosis": None,
            "narrative": None,
            "metadata": {
                "executed_specialists": list(
                    state.metadata.get(
                        "executed_specialists",
                        (),
                    )
                ),
                "secondary_requested": list(
                    state.metadata.get(
                        "secondary_requested",
                        (),
                    )
                ),
                "secondary_accepted": list(
                    state.metadata.get(
                        "secondary_accepted",
                        (),
                    )
                ),
                "max_specialists": (
                    state.budget.max_specialists
                ),
                "max_rounds": (
                    state.budget.max_rounds
                ),
                "max_actions": (
                    state.budget.max_actions
                ),
            },
        }

        if final_diagnosis is not None:
            snapshot[
                "correlated_claims"
            ] = [
                self._serialize_claim(claim)
                for claim
                in final_diagnosis.claims
            ]

            snapshot["conflicts"] = [
                self._serialize_conflict(
                    conflict
                )
                for conflict
                in final_diagnosis.conflicts
            ]

            snapshot[
                "final_diagnosis"
            ] = self._serialize_final_diagnosis(
                final_diagnosis
            )

        if narrative is not None:
            snapshot[
                "narrative"
            ] = self._serialize_narrative(
                narrative
            )

        return self._json_safe(snapshot)

    def _serialize_run(
        self,
        run,
    ) -> dict:
        loop = run.loop_result

        return {
            "specialist_slug": (
                run.specialist_slug
            ),
            "task_id": run.task.task_id,
            "status": (
                run.result.status.value
            ),
            "confidence": (
                run.result.confidence
            ),
            "summary": run.result.summary,
            "recommended_next_specialists": list(
                run.result
                .recommended_next_specialists
            ),
            "rounds_completed": (
                loop.rounds_completed
                if loop is not None
                else None
            ),
            "actions_executed": (
                loop.actions_executed
                if loop is not None
                else 0
            ),
            "stop_reason": (
                loop.stop_reason.value
                if loop is not None
                else None
            ),
            "evidence_ids": list(
                run.result.evidence_ids
            ),
            "metadata": dict(
                run.result.metadata
                or {}
            ),
        }

    def _serialize_evidence(
        self,
        item,
    ) -> dict:
        return {
            "evidence_id": item.evidence_id,
            "kind": item.kind.value,
            "title": item.title,
            "source_id": item.source_id,
            "excerpt": item.excerpt,
            "metadata": dict(
                item.metadata
                or {}
            ),
        }

    def _serialize_claim(
        self,
        claim,
    ) -> dict:
        return {
            "claim_id": claim.claim_id,
            "title": claim.title,
            "description": (
                claim.description
            ),
            "certainty": (
                claim.certainty.value
            ),
            "confidence": (
                claim.confidence
            ),
            "specialist_slugs": list(
                claim.specialist_slugs
            ),
            "evidence_ids": list(
                claim.evidence_ids
            ),
            "knowledge_source_ids": list(
                claim.knowledge_source_ids
            ),
            "missing_evidence": list(
                claim.missing_evidence
            ),
            "metadata": dict(
                claim.metadata
                or {}
            ),
        }

    def _serialize_conflict(
        self,
        conflict,
    ) -> dict:
        return {
            "conflict_id": (
                conflict.conflict_id
            ),
            "title": conflict.title,
            "diagnostic_states": list(
                conflict.diagnostic_states
            ),
            "specialist_slugs": list(
                conflict.specialist_slugs
            ),
            "evidence_ids": list(
                conflict.evidence_ids
            ),
            "source_finding_ids": list(
                conflict.source_finding_ids
            ),
            "description": (
                conflict.description
            ),
        }

    def _serialize_final_diagnosis(
        self,
        diagnosis: FinalDiagnosis,
    ) -> dict:
        return {
            "investigation_id": (
                diagnosis.investigation_id
            ),
            "summary": diagnosis.summary,
            "confirmed_count": (
                diagnosis.confirmed_count
            ),
            "probable_count": (
                diagnosis.probable_count
            ),
            "unknown_count": (
                diagnosis.unknown_count
            ),
            "conflict_count": (
                diagnosis.conflict_count
            ),
            "evidence_ids": list(
                diagnosis.evidence_ids
            ),
            "specialist_slugs": list(
                diagnosis.specialist_slugs
            ),
            "metadata": dict(
                diagnosis.metadata
                or {}
            ),
        }

    def _serialize_narrative(
        self,
        narrative: FinalDiagnosisNarrative,
    ) -> dict:
        return {
            "summary": narrative.summary,
            "claim_ids": list(
                narrative.claim_ids
            ),
            "conflict_ids": list(
                narrative.conflict_ids
            ),
            "operator_notes": list(
                narrative.operator_notes
            ),
            "provider_name": (
                narrative.provider_name
            ),
            "model_name": (
                narrative.model_name
            ),
            "used_fallback": (
                narrative.used_fallback
            ),
            "metadata": dict(
                narrative.metadata
                or {}
            ),
        }

    def _json_safe(
        self,
        value: Any,
    ) -> Any:
        if value is None:
            return None

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ):
            return value

        if isinstance(value, dict):
            return {
                str(key): self._json_safe(
                    item
                )
                for key, item
                in value.items()
            }

        if isinstance(
            value,
            (list, tuple, set),
        ):
            return [
                self._json_safe(item)
                for item in value
            ]

        if hasattr(value, "value"):
            return self._json_safe(
                value.value
            )

        if hasattr(
            value,
            "isoformat",
        ):
            try:
                return value.isoformat()
            except Exception:
                pass

        try:
            return self._json_safe(
                asdict(value)
            )
        except (
            TypeError,
            ValueError,
        ):
            return str(value)
