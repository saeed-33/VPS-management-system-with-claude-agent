from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from app.capabilities.investigation.correlation import CrossSpecialistCorrelator
from app.capabilities.investigation.execution_contracts import (
    InvestigationExecutionResult,
    InvestigationSpecialistRun,
)
from app.capabilities.investigation.final_diagnosis_synthesizer import (
    FinalDiagnosisSynthesizer,
)
from app.capabilities.investigation.runtime_snapshot_service import (
    InvestigationRuntimeSnapshotService,
)
from app.capabilities.investigation.specialist_investigation_loop import (
    SpecialistInvestigationLoopResult,
    SpecialistLoopStopReason,
)
from app.core.contracts.investigation import (
    EvidenceKind,
    EvidenceReference,
    InvestigationBudget,
    InvestigationFinding,
    InvestigationHypothesis,
    InvestigationStatus,
    ServerInvestigationState,
    SpecialistResult,
    SpecialistTask,
    SpecialistTaskStatus,
)
from app.infrastructure.database.repositories.investigation_repository import (
    InvestigationRepository,
)


class SpecialistExecutionInProgress(RuntimeError):
    pass


class SpecialistExecutionService:
    """Own the reserve -> execute -> atomic finalize lifecycle."""

    def __init__(
        self,
        *,
        repository: InvestigationRepository,
        snapshot_service: InvestigationRuntimeSnapshotService,
        correlator: CrossSpecialistCorrelator | None = None,
        synthesizer: FinalDiagnosisSynthesizer | None = None,
    ) -> None:
        self._repository = repository
        self._snapshot_service = snapshot_service
        self._correlator = correlator or CrossSpecialistCorrelator()
        self._synthesizer = synthesizer or FinalDiagnosisSynthesizer()

    def reserve_with_token(self, *, investigation_id: str, specialist_slug: str) -> dict:
        token = str(uuid4())
        result = self._repository.reserve_specialist(
            investigation_id=investigation_id,
            specialist_slug=specialist_slug,
            ownership_token=token,
        )
        if result["status"] == "reserved":
            result["ownership_token"] = token
        return result

    async def finalize(
        self,
        *,
        task: SpecialistTask,
        loop_result: SpecialistInvestigationLoopResult,
        selected_specialists: tuple[str, ...],
        ownership_token: str,
    ) -> dict:
        model = self._repository.finalize_specialist(
            investigation_id=task.investigation_id,
            specialist_slug=task.specialist_id,
            ownership_token=ownership_token,
            merge=lambda current, metadata: self._snapshot_service.merge_specialist_result(
                model=current,
                metadata=metadata,
                task=task,
                loop_result=loop_result,
                selected_specialists=selected_specialists,
            ),
        )
        detail = dict(model.investigation_metadata or {})
        snapshot = dict(detail.get("runtime_snapshot") or {})

        if snapshot.get("status") == InvestigationStatus.COMPLETED.value:
            execution = self._execution_from_snapshot(model, snapshot)
            diagnosis = self._correlator.correlate(execution)
            # The narrative call is intentionally after the short DB finalize
            # transaction. It cannot create claims or Evidence.
            narrative = await self._synthesizer.synthesize(diagnosis)
            model = self._repository.persist_finalization(
                investigation_id=task.investigation_id,
                merge=lambda current, metadata: self._snapshot_service.merge_finalization(
                    metadata=metadata,
                    final_diagnosis=diagnosis,
                    narrative=narrative,
                ),
            )
            detail = dict(model.investigation_metadata or {})
            snapshot = dict(detail.get("runtime_snapshot") or {})

        return {
            "status": "persisted",
            "run": next(
                item for item in snapshot.get("specialist_runs", [])
                if item.get("specialist_slug") == task.specialist_id
            ),
            "snapshot": snapshot,
            "model": model,
        }

    async def finalize_failure(
        self,
        *,
        task: SpecialistTask,
        reason: str,
        selected_specialists: tuple[str, ...],
        ownership_token: str,
    ) -> dict:
        result = SpecialistResult(
            task_id=task.task_id,
            specialist_id=task.specialist_id,
            status=SpecialistTaskStatus.FAILED,
            summary=f"Specialist execution failed: {reason[:500]}",
            confidence=0.0,
            metadata={"failure_reason": reason[:1000]},
        )
        loop_result = SpecialistInvestigationLoopResult(
            final_result=result,
            evidence=(),
            rounds_completed=0,
            actions_executed=0,
            investigation_actions_used=0,
            stop_reason=SpecialistLoopStopReason.NO_EVIDENCE_COLLECTED,
            provider="unknown",
            model="unknown",
            traces=(),
        )
        return await self.finalize(
            task=task,
            loop_result=loop_result,
            selected_specialists=selected_specialists,
            ownership_token=ownership_token,
        )

    def _execution_from_snapshot(self, model, snapshot: dict) -> InvestigationExecutionResult:
        evidence = tuple(
            EvidenceReference(
                evidence_id=item["evidence_id"],
                kind=EvidenceKind(item.get("kind", EvidenceKind.COMMAND_RESULT.value)),
                title=item.get("title", item["evidence_id"]),
                source_id=item.get("source_id"),
                excerpt=item.get("excerpt"),
                metadata=dict(item.get("metadata") or {}),
            )
            for item in snapshot.get("evidence", [])
            if isinstance(item, dict) and item.get("evidence_id")
        )
        runs = tuple(self._run_from_record(model, item) for item in snapshot.get("specialist_runs", []))
        state = ServerInvestigationState(
            investigation_id=model.investigation_id,
            server_id=model.server_id,
            report_id=model.report_id,
            analysis_id=model.analysis_id,
            status=InvestigationStatus.COMPLETED,
            budget=InvestigationBudget(
                max_specialists=model.max_specialists,
                max_rounds=model.max_rounds,
                max_actions=model.max_actions,
            ),
            evidence=list(evidence),
            metadata=dict(snapshot.get("metadata") or {}),
        )
        return InvestigationExecutionResult(
            state=state,
            runs=runs,
            investigation_actions_used=int(snapshot.get("actions_used") or 0),
        )

    def _run_from_record(self, model, record: dict) -> InvestigationSpecialistRun:
        task_data = dict(record.get("task") or {})
        slug = str(record["specialist_slug"])
        task = SpecialistTask(
            task_id=str(record["task_id"]),
            investigation_id=model.investigation_id,
            server_id=int(task_data.get("server_id", model.server_id)),
            report_id=int(task_data.get("report_id", model.report_id)),
            specialist_id=slug,
            objective=str(task_data.get("objective", "Persisted Specialist execution")),
            round_number=int(task_data.get("round_number", 1)),
            status=SpecialistTaskStatus.RUNNING,
            metadata=dict(task_data.get("metadata") or {}),
        )
        findings = tuple(
            InvestigationFinding(
                finding_id=str(item["finding_id"]),
                title=str(item["title"]),
                description=str(item["description"]),
                confidence=float(item.get("confidence", 0.0)),
                evidence_ids=tuple(item.get("evidence_ids") or ()),
                knowledge_source_ids=tuple(item.get("knowledge_source_ids") or ()),
                missing_evidence=tuple(item.get("missing_evidence") or ()),
                metadata=dict(item.get("metadata") or {}),
            )
            for item in record.get("findings", [])
        )
        hypotheses = tuple(
            InvestigationHypothesis(
                hypothesis_id=str(item["hypothesis_id"]),
                statement=str(item["statement"]),
                confidence=float(item.get("confidence", 0.0)),
                supporting_evidence_ids=tuple(item.get("supporting_evidence_ids") or ()),
                contradicting_evidence_ids=tuple(item.get("contradicting_evidence_ids") or ()),
                metadata=dict(item.get("metadata") or {}),
            )
            for item in record.get("hypotheses", [])
        )
        result = SpecialistResult(
            task_id=task.task_id,
            specialist_id=slug,
            status=SpecialistTaskStatus(str(record.get("status", "failed"))),
            summary=str(record.get("summary", "Persisted Specialist result")),
            confidence=float(record.get("confidence", 0.0)),
            findings=findings,
            hypotheses=hypotheses,
            ruled_out=tuple(record.get("ruled_out") or ()),
            evidence_ids=tuple(record.get("evidence_ids") or ()),
            knowledge_source_ids=tuple(record.get("knowledge_source_ids") or ()),
            missing_evidence=tuple(record.get("missing_evidence") or ()),
            recommended_next_specialists=tuple(record.get("recommended_next_specialists") or ()),
            metadata=dict(record.get("metadata") or {}),
        )
        return InvestigationSpecialistRun(
            specialist_slug=slug,
            task=task,
            result=result,
            loop_result=None,
        )
