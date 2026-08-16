"""
جزء من Investigation/Specialist لتوجيه التحقيق وجمع Evidence وبناء التشخيص.

الموقع في المعمارية: Application capability / investigation.
يُستدعى بواسطة: MCP أو Analysis workflow.
يعتمد مباشرة على: app.capabilities.investigation.correlation، app.capabilities.investigation.final_diagnosis_synthesizer، app.capabilities.investigation.execution_contracts، app.core.contracts.investigation، app.infrastructure.database.repositories.investigation_repository.
الحد المعماري: لا يتجاوز Diagnostic Policy؛ Python يتحقق وينفذ collection.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.capabilities.investigation.correlation import FinalDiagnosis
from app.capabilities.investigation.final_diagnosis_synthesizer import (
    FinalDiagnosisNarrative,
)
from app.capabilities.investigation.execution_contracts import (
    InvestigationExecutionResult,
)
from app.core.contracts.investigation import (
    EvidenceKind,
    EvidenceReference,
)
from app.infrastructure.database.repositories.investigation_repository import (
    InvestigationRepository,
)


class InvestigationRuntimeSnapshotService:
    """
    Persist a bounded operator-facing snapshot of accepted runtime state.

    The snapshot is intentionally a read projection, not a second
    runtime state store. Runtime objects are converted
    into JSON-safe primitives before persistence.
    """

    SNAPSHOT_VERSION = "4.19.2-v1"

    def __init__(
        self,
        repository: InvestigationRepository,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: repository.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._repository = repository

    def persist(
        self,
        *,
        investigation_id: str,
        execution_result: InvestigationExecutionResult,
        final_diagnosis: FinalDiagnosis | None = None,
        narrative: FinalDiagnosisNarrative | None = None,
    ):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى persist؛ المدخلات المهمة: investigation_id، execution_result، final_diagnosis، narrative.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if not investigation_id.strip():
            raise ValueError(
                "investigation_id must not be empty."
            )

        runtime_id = (
            execution_result
            .state
            .investigation_id
        )

        snapshot = self.build_snapshot(
            execution_result=execution_result,
            final_diagnosis=final_diagnosis,
            narrative=narrative,
        )

        def merge(model, metadata):
            """
            ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

            تُستدعى عندما يصل workflow إلى merge؛ المدخلات المهمة: model، metadata.
            تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
            قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
            """
            current = dict(metadata.get("runtime_snapshot") or {})
            if current:
                snapshot["specialist_runs"] = self._merge_by_key(
                    current.get("specialist_runs", []),
                    snapshot.get("specialist_runs", []),
                    key="task_id",
                )
                snapshot["evidence"] = self._merge_by_key(
                    current.get("evidence", []),
                    snapshot.get("evidence", []),
                    key="evidence_id",
                )
                snapshot["evidence_count"] = len(snapshot["evidence"])
                snapshot["actions_used"] = max(
                    int(current.get("actions_used") or 0),
                    int(snapshot.get("actions_used") or 0),
                )
                for key in ("correlated_claims", "conflicts", "final_diagnosis", "narrative"):
                    if not snapshot.get(key) and current.get(key):
                        snapshot[key] = current[key]
                snapshot["metadata"] = {
                    **dict(current.get("metadata") or {}),
                    **dict(snapshot.get("metadata") or {}),
                }
            metadata["runtime_snapshot"] = self._json_safe(snapshot)
            metadata["runtime_snapshot_version"] = self.SNAPSHOT_VERSION
            metadata["runtime_investigation_id"] = runtime_id
            return metadata

        if hasattr(self._repository, "merge_runtime_snapshot"):
            return self._repository.merge_runtime_snapshot(
                investigation_id=investigation_id,
                status=execution_result.state.status.value,
                merge=merge,
            )

        # Test doubles and legacy adapters may only expose the old method.
        # Production repository composition always takes the locked merge path.
        model = self._repository.get_by_investigation_id(investigation_id)
        if model is None:
            raise ValueError(f"Investigation not found: {investigation_id}")
        return self._repository.update_runtime_snapshot(
            investigation_id=investigation_id,
            status=execution_result.state.status.value,
            metadata=merge(model, dict(model.investigation_metadata or {})),
        )

    @staticmethod
    def _merge_by_key(existing: list, incoming: list, *, key: str) -> list:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _merge_by_key؛ المدخلات المهمة: existing، incoming، key.
        تعيد list أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        merged = {item.get(key): dict(item) for item in existing if isinstance(item, dict) and item.get(key)}
        for item in incoming:
            if isinstance(item, dict) and item.get(key):
                merged[item[key]] = dict(item)
        return list(merged.values())

    def build_snapshot(
        self,
        *,
        execution_result: InvestigationExecutionResult,
        final_diagnosis: FinalDiagnosis | None = None,
        narrative: FinalDiagnosisNarrative | None = None,
    ) -> dict:
        """
        يبني DTO أو dependency graph من المدخلات ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى build_snapshot؛ المدخلات المهمة: execution_result، final_diagnosis، narrative.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        state = execution_result.state

        specialist_runs = tuple(
            self._serialize_run(run)
            for run in execution_result.runs
        )

        evidence = tuple(
            self._serialize_evidence(
                item,
                investigation_id=state.investigation_id,
                server_id=state.server_id,
                report_id=state.report_id,
            )
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
                execution_result
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

    def merge_specialist_result(
        self,
        *,
        model,
        metadata: dict,
        task,
        loop_result,
        selected_specialists: tuple[str, ...],
    ) -> tuple[str, dict]:
        """Merge one accepted loop result into the latest locked snapshot."""
        merged = dict(metadata)
        snapshot = dict(merged.get("runtime_snapshot") or {})
        if not snapshot:
            snapshot = self._empty_snapshot(model)

        runs = list(snapshot.get("specialist_runs") or [])
        if any(item.get("specialist_slug") == task.specialist_id for item in runs):
            return str(model.status), merged

        evidence = list(snapshot.get("evidence") or [])
        evidence_by_id = {item.get("evidence_id"): item for item in evidence}
        for item in loop_result.evidence:
            evidence_by_id[item.evidence_id] = self._serialize_evidence(
                item,
                investigation_id=model.investigation_id,
                server_id=model.server_id,
                report_id=model.report_id,
            )

        runs.append(self._serialize_accepted_run(task, loop_result))
        snapshot["specialist_runs"] = runs
        snapshot["evidence"] = list(evidence_by_id.values())
        snapshot["evidence_count"] = len(snapshot["evidence"])
        snapshot["actions_used"] = max(
            int(snapshot.get("actions_used") or 0),
            int(loop_result.investigation_actions_used),
        )
        all_terminal = all(
            any(
                item.get("specialist_slug") == slug
                and item.get("status") in {"completed", "failed", "cancelled"}
                for item in runs
            )
            for slug in selected_specialists
        )
        has_failure = any(item.get("status") in {"failed", "cancelled"} for item in runs)
        snapshot["status"] = (
            "failed" if all_terminal and has_failure
            else "completed" if all_terminal
            else "investigating"
        )

        runtime_metadata = dict(snapshot.get("metadata") or {})
        terminal = [
            item.get("specialist_slug")
            for item in runs
            if item.get("status") in {"completed", "failed", "cancelled"}
        ]
        completed = [
            item.get("specialist_slug")
            for item in runs
            if item.get("status") == "completed"
        ]
        failed = [
            item.get("specialist_slug")
            for item in runs
            if item.get("status") in {"failed", "cancelled"}
        ]
        runtime_metadata["selected_specialists"] = list(selected_specialists)
        runtime_metadata["completed_specialists"] = list(dict.fromkeys(completed))
        runtime_metadata["terminal_specialists"] = list(dict.fromkeys(terminal))
        runtime_metadata["failed_specialists"] = list(dict.fromkeys(failed))
        runtime_metadata["remaining_specialists"] = [
            slug for slug in selected_specialists if slug not in terminal
        ]
        runtime_metadata["executed_specialists"] = list(dict.fromkeys(terminal))
        snapshot["metadata"] = runtime_metadata
        # A failed or cancelled reservation is persisted for continuity, but
        # it is not an accepted Specialist runtime result.  Keep this flag
        # tied to at least one successfully finalized Specialist run.
        snapshot["runtime_available"] = bool(completed)
        snapshot["final_diagnosis_available"] = isinstance(snapshot.get("final_diagnosis"), dict)
        merged["runtime_snapshot"] = self._json_safe(snapshot)
        merged["runtime_snapshot_version"] = self.SNAPSHOT_VERSION
        merged["runtime_investigation_id"] = model.investigation_id
        return snapshot["status"], merged

    def merge_finalization(
        self,
        *,
        metadata: dict,
        final_diagnosis: FinalDiagnosis,
        narrative: FinalDiagnosisNarrative,
    ) -> tuple[str, dict]:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى merge_finalization؛ المدخلات المهمة: metadata، final_diagnosis، narrative.
        تعيد tuple[str, dict] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        merged = dict(metadata)
        snapshot = dict(merged.get("runtime_snapshot") or {})
        snapshot["correlated_claims"] = [self._serialize_claim(item) for item in final_diagnosis.claims]
        snapshot["conflicts"] = [self._serialize_conflict(item) for item in final_diagnosis.conflicts]
        snapshot["final_diagnosis"] = self._serialize_final_diagnosis(final_diagnosis)
        snapshot["narrative"] = self._serialize_narrative(narrative)
        snapshot["runtime_available"] = True
        snapshot["final_diagnosis_available"] = True
        snapshot["status"] = "completed"
        merged["runtime_snapshot"] = self._json_safe(snapshot)
        merged["runtime_snapshot_version"] = self.SNAPSHOT_VERSION
        return "completed", merged

    def _empty_snapshot(self, model) -> dict:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _empty_snapshot؛ المدخلات المهمة: model.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return {
            "version": self.SNAPSHOT_VERSION,
            "status": "investigating",
            "actions_used": 0,
            "evidence_count": 0,
            "specialist_runs": [],
            "evidence": [],
            "correlated_claims": [],
            "conflicts": [],
            "final_diagnosis": None,
            "narrative": None,
            "runtime_available": False,
            "final_diagnosis_available": False,
            "metadata": {
                "max_specialists": model.max_specialists,
                "max_rounds": model.max_rounds,
                "max_actions": model.max_actions,
            },
        }

    def _serialize_accepted_run(self, task, loop_result) -> dict:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _serialize_accepted_run؛ المدخلات المهمة: task، loop_result.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        result = loop_result.final_result
        return {
            "specialist_slug": task.specialist_id,
            "task_id": task.task_id,
            "task": {
                "server_id": task.server_id,
                "report_id": task.report_id,
                "objective": task.objective,
                "round_number": task.round_number,
                "metadata": dict(task.metadata or {}),
            },
            "status": result.status.value,
            "confidence": result.confidence,
            "summary": result.summary,
            "findings": [self._serialize_finding(item) for item in result.findings],
            "hypotheses": [self._serialize_hypothesis(item) for item in result.hypotheses],
            "ruled_out": list(result.ruled_out),
            "recommended_next_specialists": list(result.recommended_next_specialists),
            "evidence_ids": list(result.evidence_ids),
            "knowledge_source_ids": list(result.knowledge_source_ids),
            "missing_evidence": list(result.missing_evidence),
            "rounds_completed": loop_result.rounds_completed,
            "actions_executed": loop_result.actions_executed,
            "investigation_actions_used": loop_result.investigation_actions_used,
            "stop_reason": loop_result.stop_reason.value,
            "provider": loop_result.provider,
            "model": loop_result.model,
            "metadata": dict(result.metadata or {}),
        }

    def _serialize_finding(self, finding) -> dict:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _serialize_finding؛ المدخلات المهمة: finding.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return {
            "finding_id": finding.finding_id,
            "title": finding.title,
            "description": finding.description,
            "confidence": finding.confidence,
            "evidence_ids": list(finding.evidence_ids),
            "knowledge_source_ids": list(finding.knowledge_source_ids),
            "missing_evidence": list(finding.missing_evidence),
            "metadata": dict(finding.metadata or {}),
        }

    def _serialize_hypothesis(self, hypothesis) -> dict:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _serialize_hypothesis؛ المدخلات المهمة: hypothesis.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return {
            "hypothesis_id": hypothesis.hypothesis_id,
            "statement": hypothesis.statement,
            "confidence": hypothesis.confidence,
            "supporting_evidence_ids": list(hypothesis.supporting_evidence_ids),
            "contradicting_evidence_ids": list(hypothesis.contradicting_evidence_ids),
            "metadata": dict(hypothesis.metadata or {}),
        }

    def _serialize_run(
        self,
        run,
    ) -> dict:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _serialize_run؛ المدخلات المهمة: run.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        *,
        investigation_id: str,
        server_id: int,
        report_id: int,
    ) -> dict:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _serialize_evidence؛ المدخلات المهمة: item، investigation_id، server_id، report_id.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        metadata = dict(item.metadata or {})
        metadata.setdefault(
            "investigation_id",
            investigation_id,
        )
        metadata.setdefault("server_id", server_id)
        metadata.setdefault("report_id", report_id)

        return {
            "evidence_id": item.evidence_id,
            "kind": item.kind.value,
            "title": item.title,
            "source_id": item.source_id,
            "excerpt": item.excerpt,
            "metadata": metadata,
        }

    def _serialize_claim(
        self,
        claim,
    ) -> dict:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _serialize_claim؛ المدخلات المهمة: claim.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _serialize_conflict؛ المدخلات المهمة: conflict.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _serialize_final_diagnosis؛ المدخلات المهمة: diagnosis.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _serialize_narrative؛ المدخلات المهمة: narrative.
        تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _json_safe؛ المدخلات المهمة: value.
        تعيد Any أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
