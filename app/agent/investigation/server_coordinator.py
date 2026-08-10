from __future__ import annotations

from dataclasses import dataclass, replace
from uuid import uuid4

from app.agent.investigation.contracts import (
    InvestigationBudget,
    InvestigationStatus,
    ServerInvestigationState,
    SpecialistResult,
    SpecialistTask,
    SpecialistTaskStatus,
)
from app.agent.investigation.investigation_router import InvestigationRoutingDecision
from app.agent.investigation.specialist_investigation_loop import (
    SpecialistInvestigationLoop,
    SpecialistInvestigationLoopResult,
)
from app.agent.investigation.specialist_registry import (
    SpecialistRegistry,
    SpecialistRegistrySnapshot,
)


@dataclass(slots=True, frozen=True)
class ServerCoordinatorSpecialistRun:
    specialist_slug: str
    task: SpecialistTask
    result: SpecialistResult
    loop_result: SpecialistInvestigationLoopResult | None


@dataclass(slots=True, frozen=True)
class ServerCoordinatorResult:
    state: ServerInvestigationState
    runs: tuple[ServerCoordinatorSpecialistRun, ...]
    investigation_actions_used: int


class ServerCoordinator:
    """Coordinate selected Specialists for one server.

    Phase 4.15 is sequential by design. Parallel execution is Phase 4.16.
    """

    def __init__(
        self,
        *,
        specialist_registry: SpecialistRegistry,
        specialist_loop: SpecialistInvestigationLoop,
    ) -> None:
        self._specialist_registry = specialist_registry
        self._specialist_loop = specialist_loop

    async def run(
        self,
        *,
        server_id: int,
        report_id: int,
        analysis_id: int | None,
        routing_decision: InvestigationRoutingDecision,
        budget: InvestigationBudget | None = None,
        initial_analysis_summary: str | None = None,
        initial_analysis_issues: tuple[dict, ...] = (),
        incident_contexts=(),
        initial_evidence=(),
        investigation_id: str | None = None,
        registry_snapshot: SpecialistRegistrySnapshot | None = None,
    ) -> ServerCoordinatorResult:
        budget = budget or InvestigationBudget()
        snapshot = registry_snapshot or self._specialist_registry.snapshot()

        state = ServerInvestigationState(
            investigation_id=investigation_id or str(uuid4()),
            server_id=server_id,
            report_id=report_id,
            analysis_id=analysis_id,
            status=InvestigationStatus.CREATED,
            budget=budget,
            detected_domains=list(routing_decision.detected_domains),
        )

        for item in initial_evidence:
            state.add_evidence(item)

        if (
            not routing_decision.should_investigate
            or not routing_decision.selected_specialists
        ):
            state.status = InvestigationStatus.COMPLETED
            state.metadata["coordinator_stop_reason"] = (
                "investigation_not_required"
                if not routing_decision.should_investigate
                else "no_selected_specialists"
            )
            return ServerCoordinatorResult(
                state=state,
                runs=(),
                investigation_actions_used=0,
            )

        selected = routing_decision.selected_specialists[: budget.max_specialists]
        allowed_slugs = tuple(item.slug for item in snapshot.definitions)
        state.status = InvestigationStatus.INVESTIGATING
        runs: list[ServerCoordinatorSpecialistRun] = []
        global_actions_used = 0

        for match in selected:
            specialist = snapshot.get_by_slug(match.specialist_slug)
            task = SpecialistTask(
                task_id=f"{state.investigation_id}:{match.specialist_slug}:1",
                investigation_id=state.investigation_id,
                server_id=server_id,
                report_id=report_id,
                specialist_id=match.specialist_slug,
                objective=self._build_objective(
                    specialist_name=match.specialist_name,
                    matched_domains=match.matched_domains,
                    matched_issue_indexes=match.matched_issue_indexes,
                ),
                trigger_issue_ids=tuple(
                    f"analysis-issue:{index}"
                    for index in match.matched_issue_indexes
                ),
                evidence_ids=tuple(item.evidence_id for item in state.evidence),
                knowledge_topics=(
                    specialist.knowledge_topics if specialist is not None else ()
                ),
                status=SpecialistTaskStatus.RUNNING,
            )
            state.add_task(task)

            if specialist is None:
                failed = SpecialistResult(
                    task_id=task.task_id,
                    specialist_id=task.specialist_id,
                    status=SpecialistTaskStatus.FAILED,
                    summary=(
                        "Selected Specialist is no longer enabled or available "
                        "in the registry snapshot."
                    ),
                    confidence=0.0,
                    missing_evidence=("Enabled Specialist runtime definition.",),
                    metadata={"coordinator_failure": "specialist_unavailable"},
                )
                state.add_result(failed)
                runs.append(
                    ServerCoordinatorSpecialistRun(
                        specialist_slug=match.specialist_slug,
                        task=replace(task, status=SpecialistTaskStatus.FAILED),
                        result=failed,
                        loop_result=None,
                    )
                )
                continue

            try:
                loop_result = await self._specialist_loop.run(
                    task=task,
                    specialist=specialist,
                    investigation_budget=budget,
                    detected_domains=tuple(routing_decision.detected_domains),
                    initial_evidence=tuple(state.evidence),
                    initial_analysis_summary=initial_analysis_summary,
                    initial_analysis_issues=initial_analysis_issues,
                    incident_contexts=incident_contexts,
                    allowed_specialist_slugs=allowed_slugs,
                    investigation_actions_used=global_actions_used,
                )
                global_actions_used = loop_result.investigation_actions_used

                for evidence in loop_result.evidence:
                    if not any(
                        item.evidence_id == evidence.evidence_id
                        for item in state.evidence
                    ):
                        state.add_evidence(evidence)

                result = loop_result.final_result
                state.add_result(result)
                runs.append(
                    ServerCoordinatorSpecialistRun(
                        specialist_slug=specialist.slug,
                        task=replace(task, status=result.status),
                        result=result,
                        loop_result=loop_result,
                    )
                )
            except Exception as exc:
                failed = SpecialistResult(
                    task_id=task.task_id,
                    specialist_id=task.specialist_id,
                    status=SpecialistTaskStatus.FAILED,
                    summary=(
                        "Specialist investigation failed before a valid result "
                        "was produced."
                    ),
                    confidence=0.0,
                    metadata={
                        "coordinator_failure": type(exc).__name__,
                        "error": str(exc),
                    },
                )
                state.add_result(failed)
                runs.append(
                    ServerCoordinatorSpecialistRun(
                        specialist_slug=specialist.slug,
                        task=replace(task, status=SpecialistTaskStatus.FAILED),
                        result=failed,
                        loop_result=None,
                    )
                )

        state.metadata["investigation_actions_used"] = global_actions_used
        state.metadata["selected_specialists"] = [
            item.specialist_slug for item in selected
        ]
        state.metadata["completed_specialists"] = [
            item.specialist_slug
            for item in runs
            if item.result.status == SpecialistTaskStatus.COMPLETED
        ]
        state.metadata["failed_specialists"] = [
            item.specialist_slug
            for item in runs
            if item.result.status == SpecialistTaskStatus.FAILED
        ]

        if runs and all(
            item.result.status == SpecialistTaskStatus.FAILED for item in runs
        ):
            state.status = InvestigationStatus.FAILED
        else:
            state.status = InvestigationStatus.COMPLETED

        return ServerCoordinatorResult(
            state=state,
            runs=tuple(runs),
            investigation_actions_used=global_actions_used,
        )

    @staticmethod
    def _build_objective(
        *,
        specialist_name: str,
        matched_domains: tuple[str, ...],
        matched_issue_indexes: tuple[int, ...],
    ) -> str:
        domains = ", ".join(matched_domains) or "assigned domains"
        refs = (
            ", ".join(str(index) for index in matched_issue_indexes)
            if matched_issue_indexes
            else "routing evidence"
        )
        return (
            f"Investigate the server evidence relevant to {domains} as "
            f"{specialist_name}. Determine what is confirmed, what remains "
            f"uncertain, and what live evidence supports the conclusion. "
            f"Routing references: {refs}."
        )
