from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from app.mcp.schemas import (
    ProjectToolCall,
    ProjectToolDefinition,
    ProjectToolResult,
)
from app.mcp.serializers import (
    serialize_analysis,
    serialize_incident_context,
    serialize_knowledge_context,
    serialize_monitoring_report_data,
    serialize_profile,
    serialize_report_details,
    serialize_server,
    serialize_specialist_definition,
    serialize_specialist_loop_result,
    serialize_value,
)
from app.tools.catalog import (
    group_definitions,
)
from app.domain.investigation.contracts import (
    InvestigationBudget,
    SpecialistTask,
    SpecialistTaskStatus,
)
from app.domain.analysis.retrieval.report_fingerprint import (
    ReportFingerprintService,
)
from app.domain.analysis.retrieval.report_normalizer import (
    ReportNormalizer,
)


ToolHandler = Callable[
    [dict[str, Any]],
    Awaitable[ProjectToolResult],
]


class ProjectMcpToolBoundary:
    def __init__(
        self,
        *,
        server_service,
        monitoring_profile_service,
        monitoring_service,
        report_query_service,
        analysis_orchestrator=None,
        analysis_repository=None,
        incident_retriever=None,
        knowledge_retriever=None,
        investigation_router=None,
        investigation_persistence_service=None,
        investigation_read_service=None,
        specialist_registry=None,
        specialist_investigation_loop=None,
        remediation_service=None,
    ) -> None:
        self._server_service = server_service
        self._monitoring_profile_service = (
            monitoring_profile_service
        )
        self._monitoring_service = monitoring_service
        self._report_query_service = (
            report_query_service
        )
        self._analysis_orchestrator = (
            analysis_orchestrator
        )
        self._analysis_repository = (
            analysis_repository
        )
        self._incident_retriever = (
            incident_retriever
        )
        self._knowledge_retriever = (
            knowledge_retriever
        )
        self._investigation_router = (
            investigation_router
        )
        self._investigation_persistence_service = (
            investigation_persistence_service
        )
        self._investigation_read_service = (
            investigation_read_service
        )
        self._specialist_registry = (
            specialist_registry
        )
        self._specialist_investigation_loop = (
            specialist_investigation_loop
        )
        self._remediation_service = (
            remediation_service
        )
        self._normalizer = ReportNormalizer()
        self._fingerprint_service = (
            ReportFingerprintService()
        )

        self._definitions = {
            item.tool_id: item
            for item in self._build_definitions()
        }

        self._handlers: dict[
            str,
            ToolHandler,
        ] = {
            "get_server_context": (
                self._get_server_context
            ),
            "get_monitoring_profile": (
                self._get_monitoring_profile
            ),
            "run_monitoring": (
                self._run_monitoring
            ),
            "get_report": self._get_report,
            "get_latest_report": (
                self._get_latest_report
            ),
            "find_exact_report_match": (
                self._find_exact_report_match
            ),
            "search_similar_incidents": (
                self._search_similar_incidents
            ),
            "get_top_similar_reports": (
                self._get_top_similar_reports
            ),
            "analyze_report": (
                self._analyze_report
            ),
            "get_analysis": self._get_analysis,
            "search_knowledge": (
                self._search_knowledge
            ),
            "start_investigation": (
                self._start_investigation
            ),
            "get_investigation": (
                self._get_investigation
            ),
            "get_investigation_status": (
                self._get_investigation_status
            ),
            "get_evidence": self._get_evidence,
            "get_available_specialists": (
                self._get_available_specialists
            ),
            "get_specialist_definition": (
                self._get_specialist_definition
            ),
            "run_specialist": (
                self._run_specialist
            ),
            "propose_remediation": (
                self._propose_remediation
            ),
            "create_remediation_plan": (
                self._create_remediation_plan
            ),
            "test_remediation_in_sandbox": (
                self._test_remediation_in_sandbox
            ),
            "get_sandbox_result": (
                self._get_sandbox_result
            ),
            "request_user_approval": (
                self._request_user_approval
            ),
            "apply_approved_remediation": (
                self._apply_approved_remediation
            ),
        }

    def list_tools(
        self,
    ) -> list[ProjectToolDefinition]:
        return [
            self._definitions[key]
            for key in sorted(
                self._definitions
            )
        ]

    def list_tool_groups(
        self,
    ) -> dict[str, list[ProjectToolDefinition]]:
        return group_definitions(
            self.list_tools()
        )

    async def execute(
        self,
        call: ProjectToolCall,
    ) -> ProjectToolResult:
        handler = self._handlers.get(
            call.tool_id
        )

        if handler is None:
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=False,
                error_code="unknown_tool",
                error_message=(
                    "Unknown project tool: "
                    f"{call.tool_id}"
                ),
            )

        try:
            return await handler(
                call.arguments
            )
        except ValueError as exc:
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=False,
                error_code="validation_error",
                error_message=str(exc),
            )
        except Exception as exc:
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=False,
                error_code="tool_execution_error",
                error_message=str(exc),
            )

    async def _get_server_context(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        server_id = self._required_int(
            arguments,
            "server_id",
        )

        server = self._server_service.get_server(
            server_id
        )

        return ProjectToolResult(
            tool_id="get_server_context",
            success=True,
            data={
                "server": serialize_server(
                    server
                )
            },
        )

    async def _get_monitoring_profile(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        profile_id = self._required_int(
            arguments,
            "profile_id",
        )

        profile = (
            self._monitoring_profile_service
            .get_profile(
                profile_id
            )
        )
        commands = (
            self._monitoring_profile_service
            .list_profile_commands(
                profile_id
            )
        )

        return ProjectToolResult(
            tool_id="get_monitoring_profile",
            success=True,
            data={
                "profile": serialize_profile(
                    profile,
                    commands=commands,
                )
            },
        )

    async def _run_monitoring(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        server_id = self._required_int(
            arguments,
            "server_id",
        )

        report = await self._monitoring_service.run(
            server_id
        )

        latest = self._latest_report_for_server(
            server_id
        )

        return ProjectToolResult(
            tool_id="run_monitoring",
            success=True,
            data={
                "monitoring_report": (
                    serialize_monitoring_report_data(
                        report
                    )
                ),
                "persisted_report": (
                    serialize_report_details(
                        latest
                    )
                    if latest is not None
                    else None
                ),
            },
        )

    async def _get_report(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        report_id = self._required_int(
            arguments,
            "report_id",
        )

        report = (
            self._report_query_service
            .get_report(
                report_id
            )
        )

        return ProjectToolResult(
            tool_id="get_report",
            success=True,
            data={
                "report": serialize_report_details(
                    report
                )
            },
        )

    async def _get_latest_report(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        server_id = self._required_int(
            arguments,
            "server_id",
        )

        report = self._latest_report_for_server(
            server_id
        )

        if report is None:
            return ProjectToolResult(
                tool_id="get_latest_report",
                success=False,
                error_code="report_not_found",
                error_message=(
                    "No report found for server "
                    f"{server_id}."
                ),
            )

        return ProjectToolResult(
            tool_id="get_latest_report",
            success=True,
            data={
                "report": serialize_report_details(
                    report
                )
            },
        )

    async def _find_exact_report_match(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._analysis_repository,
            "analysis_repository",
        )

        report_id = self._required_int(
            arguments,
            "report_id",
        )
        report = (
            self._report_query_service
            .get_report(report_id)
        )
        normalized = self._normalizer.normalize(
            report
        )
        fingerprint = (
            self._fingerprint_service
            .create(normalized)
        )
        match = (
            self._analysis_repository
            .find_completed_by_fingerprint(
                server_id=report.server_id,
                report_fingerprint=fingerprint,
                exclude_report_id=report_id,
            )
        )

        return ProjectToolResult(
            tool_id="find_exact_report_match",
            success=True,
            data={
                "matched": match is not None,
                "report_fingerprint": fingerprint,
                "analysis": (
                    serialize_analysis(match)
                    if match is not None
                    else None
                ),
            },
        )

    async def _search_similar_incidents(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        return await self._search_incidents(
            tool_id="search_similar_incidents",
            arguments=arguments,
        )

    async def _get_top_similar_reports(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        return await self._search_incidents(
            tool_id="get_top_similar_reports",
            arguments={
                **arguments,
                "limit": min(
                    self._optional_int(
                        arguments,
                        "limit",
                        default=3,
                    ),
                    3,
                ),
            },
        )

    async def _search_incidents(
        self,
        *,
        tool_id: str,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._incident_retriever,
            "incident_retriever",
        )

        report_id = self._required_int(
            arguments,
            "report_id",
        )
        limit = min(
            self._optional_int(
                arguments,
                "limit",
                default=3,
            ),
            3,
        )
        report = (
            self._report_query_service
            .get_report(report_id)
        )
        normalized = self._normalizer.normalize(
            report
        )
        command_set_hash = (
            self._normalizer
            .command_set_hash(report)
        )

        contexts = await (
            self._incident_retriever.retrieve(
                normalized_report=normalized,
                server_id=report.server_id,
                monitoring_profile_id=(
                    report.monitoring_profile_id
                ),
                command_set_hash=command_set_hash,
                exclude_report_id=report_id,
            )
        )

        return ProjectToolResult(
            tool_id=tool_id,
            success=True,
            data={
                "limit": limit,
                "similar_reports": [
                    serialize_incident_context(
                        item
                    )
                    for item in contexts[:limit]
                ],
            },
        )

    async def _analyze_report(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._analysis_orchestrator,
            "analysis_orchestrator",
        )
        self._require_dependency(
            self._analysis_repository,
            "analysis_repository",
        )

        report_id = self._required_int(
            arguments,
            "report_id",
        )
        force = bool(
            arguments.get("force", False)
        )
        report = (
            self._report_query_service
            .get_report(report_id)
        )
        analysis_id = await (
            self._analysis_orchestrator
            .process(
                report_id=report_id,
                server_id=report.server_id,
                force=force,
            )
        )
        analysis = (
            self._analysis_repository
            .get_by_id(analysis_id)
        )

        return ProjectToolResult(
            tool_id="analyze_report",
            success=True,
            data={
                "analysis_id": analysis_id,
                "analysis": (
                    serialize_analysis(analysis)
                    if analysis is not None
                    else None
                ),
            },
        )

    async def _get_analysis(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._analysis_repository,
            "analysis_repository",
        )

        analysis = None

        if "analysis_id" in arguments:
            analysis_id = self._required_int(
                arguments,
                "analysis_id",
            )
            analysis = (
                self._analysis_repository
                .get_by_id(analysis_id)
            )
        elif "report_id" in arguments:
            report_id = self._required_int(
                arguments,
                "report_id",
            )
            analysis = (
                self._analysis_repository
                .get_by_report_id(report_id)
            )
        else:
            raise ValueError(
                "analysis_id or report_id is required."
            )

        if analysis is None:
            return ProjectToolResult(
                tool_id="get_analysis",
                success=False,
                error_code="analysis_not_found",
                error_message="Analysis not found.",
            )

        return ProjectToolResult(
            tool_id="get_analysis",
            success=True,
            data={
                "analysis": serialize_analysis(
                    analysis
                )
            },
        )

    async def _search_knowledge(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._knowledge_retriever,
            "knowledge_retriever",
        )

        query = arguments.get("query")
        if not isinstance(query, str) or not query.strip():
            raise ValueError(
                "query must be a non-empty string."
            )

        domains = arguments.get("domains", [])
        if not isinstance(domains, list):
            raise ValueError(
                "domains must be a list."
            )

        specialist_slug = arguments.get(
            "specialist_slug"
        )
        if (
            specialist_slug is not None
            and not isinstance(specialist_slug, str)
        ):
            raise ValueError(
                "specialist_slug must be a string."
            )

        limit = min(
            self._optional_int(
                arguments,
                "limit",
                default=6,
            ),
            6,
        )

        contexts = await (
            self._knowledge_retriever.retrieve(
                query=query,
                specialist_slug=specialist_slug,
                domains=tuple(
                    str(item)
                    for item in domains
                ),
            )
        )

        return ProjectToolResult(
            tool_id="search_knowledge",
            success=True,
            data={
                "limit": limit,
                "knowledge": [
                    serialize_knowledge_context(
                        item
                    )
                    for item in contexts[:limit]
                ],
            },
        )

    async def _start_investigation(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._investigation_router,
            "investigation_router",
        )
        self._require_dependency(
            self._investigation_persistence_service,
            "investigation_persistence_service",
        )
        self._require_dependency(
            self._investigation_read_service,
            "investigation_read_service",
        )
        self._require_dependency(
            self._analysis_repository,
            "analysis_repository",
        )

        report_id = self._required_int(
            arguments,
            "report_id",
        )
        analysis_id = arguments.get(
            "analysis_id"
        )
        if analysis_id is not None and not isinstance(
            analysis_id,
            int,
        ):
            raise ValueError(
                "analysis_id must be an integer."
            )

        report = (
            self._report_query_service
            .get_report(report_id)
        )

        analysis = (
            self._analysis_repository.get_by_id(
                analysis_id
            )
            if analysis_id is not None
            else self._analysis_repository
            .get_by_report_id(report_id)
        )

        if analysis is None:
            return ProjectToolResult(
                tool_id="start_investigation",
                success=False,
                error_code="analysis_not_found",
                error_message=(
                    "Analysis is required before "
                    "starting investigation."
                ),
            )

        decision = (
            self._investigation_router
            .route(
                report=report,
                analysis=analysis,
            )
        )

        model = (
            self
            ._investigation_persistence_service
            .persist_routing_decision(
                server_id=report.server_id,
                report_id=report_id,
                analysis_id=analysis.id,
                decision=decision,
            )
        )

        detail = (
            self._investigation_read_service
            .get(model.investigation_id)
        )

        return ProjectToolResult(
            tool_id="start_investigation",
            success=True,
            data={
                "investigation": serialize_value(
                    detail
                ),
                "routing": {
                    "should_investigate": (
                        decision.should_investigate
                    ),
                    "selected_specialists": list(
                        decision.selected_slugs
                    ),
                    "candidate_specialists": list(
                        decision.candidate_slugs
                    ),
                    "detected_domains": list(
                        decision.detected_domains
                    ),
                },
            },
        )

    async def _get_investigation(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        detail = self._read_investigation(
            arguments
        )

        if detail is None:
            return ProjectToolResult(
                tool_id="get_investigation",
                success=False,
                error_code="investigation_not_found",
                error_message="Investigation not found.",
            )

        return ProjectToolResult(
            tool_id="get_investigation",
            success=True,
            data={
                "investigation": serialize_value(
                    detail
                )
            },
        )

    async def _get_investigation_status(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        detail = self._read_investigation(
            arguments
        )

        if detail is None:
            return ProjectToolResult(
                tool_id="get_investigation_status",
                success=False,
                error_code="investigation_not_found",
                error_message="Investigation not found.",
            )

        return ProjectToolResult(
            tool_id="get_investigation_status",
            success=True,
            data={
                "investigation_id": (
                    detail.investigation_id
                ),
                "status": detail.status,
                "should_investigate": (
                    detail.should_investigate
                ),
                "runtime_available": (
                    detail.runtime_available
                ),
                "final_diagnosis_available": (
                    detail.final_diagnosis_available
                ),
                "selected_specialists": [
                    candidate.specialist_slug
                    for candidate in detail.candidates
                    if candidate.is_selected
                ],
            },
        )

    async def _get_evidence(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        detail = self._read_investigation(
            arguments
        )

        if detail is None:
            return ProjectToolResult(
                tool_id="get_evidence",
                success=False,
                error_code="investigation_not_found",
                error_message="Investigation not found.",
            )

        evidence = (
            detail.runtime.evidence
            if (
                detail.runtime is not None
                and detail.runtime.evidence
            )
            else ()
        )

        return ProjectToolResult(
            tool_id="get_evidence",
            success=True,
            data={
                "investigation_id": (
                    detail.investigation_id
                ),
                "evidence": serialize_value(
                    evidence
                ),
            },
        )

    async def _get_available_specialists(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._specialist_registry,
            "specialist_registry",
        )

        domains = arguments.get("domains", [])
        if not isinstance(domains, list):
            raise ValueError(
                "domains must be a list."
            )

        snapshot = (
            self._specialist_registry.snapshot()
        )

        if domains:
            definitions = tuple(
                match.specialist
                for match in snapshot.find_by_domains(
                    domains
                )
            )
        else:
            definitions = snapshot.definitions

        return ProjectToolResult(
            tool_id="get_available_specialists",
            success=True,
            data={
                "specialists": [
                    serialize_specialist_definition(
                        item
                    )
                    for item in definitions
                ],
            },
        )

    async def _get_specialist_definition(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        specialist = self._specialist_by_slug(
            arguments
        )

        if specialist is None:
            return ProjectToolResult(
                tool_id="get_specialist_definition",
                success=False,
                error_code="specialist_not_found",
                error_message=(
                    "Enabled Specialist definition "
                    "was not found."
                ),
            )

        return ProjectToolResult(
            tool_id="get_specialist_definition",
            success=True,
            data={
                "specialist": (
                    serialize_specialist_definition(
                        specialist
                    )
                )
            },
        )

    async def _run_specialist(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._specialist_investigation_loop,
            "specialist_investigation_loop",
        )
        self._require_dependency(
            self._analysis_repository,
            "analysis_repository",
        )

        detail = self._read_investigation(
            arguments
        )
        if detail is None:
            return ProjectToolResult(
                tool_id="run_specialist",
                success=False,
                error_code="investigation_not_found",
                error_message="Investigation not found.",
            )

        specialist = self._specialist_by_slug(
            arguments
        )
        if specialist is None:
            return ProjectToolResult(
                tool_id="run_specialist",
                success=False,
                error_code="specialist_not_found",
                error_message=(
                    "Enabled Specialist definition "
                    "was not found."
                ),
            )

        selected_slugs = {
            candidate.specialist_slug
            for candidate in detail.candidates
            if candidate.is_selected
        }
        if specialist.slug not in selected_slugs:
            return ProjectToolResult(
                tool_id="run_specialist",
                success=False,
                error_code="specialist_not_selected",
                error_message=(
                    "Specialist was not selected by "
                    "the investigation routing decision."
                ),
            )

        objective = arguments.get("objective")
        if not isinstance(objective, str) or not objective.strip():
            raise ValueError(
                "objective must be a non-empty string."
            )

        analysis = (
            self._analysis_repository.get_by_id(
                detail.analysis_id
            )
            if detail.analysis_id is not None
            else self._analysis_repository
            .get_by_report_id(detail.report_id)
        )
        if analysis is None:
            return ProjectToolResult(
                tool_id="run_specialist",
                success=False,
                error_code="analysis_not_found",
                error_message=(
                    "Analysis is required before "
                    "running a Specialist."
                ),
            )

        investigation_actions_used = 0
        if detail.runtime is not None:
            investigation_actions_used = (
                detail.runtime.actions_used or 0
            )

        task = SpecialistTask(
            task_id=(
                f"{detail.investigation_id}:"
                f"{specialist.slug}:1"
            ),
            investigation_id=detail.investigation_id,
            server_id=detail.server_id,
            report_id=detail.report_id,
            specialist_id=specialist.slug,
            objective=objective.strip(),
            trigger_issue_ids=tuple(
                str(index)
                for candidate in detail.candidates
                if (
                    candidate.specialist_slug
                    == specialist.slug
                )
                for index in (
                    candidate.matched_issue_indexes
                )
            ),
            knowledge_topics=(
                specialist.knowledge_topics
            ),
            status=SpecialistTaskStatus.RUNNING,
            metadata={
                "source": "claude_code_mcp",
                "specialist_definition_id": (
                    specialist.id
                ),
            },
        )

        result = await (
            self._specialist_investigation_loop.run(
                task=task,
                specialist=specialist,
                investigation_budget=InvestigationBudget(
                    max_specialists=(
                        detail.max_specialists
                    ),
                    max_rounds=detail.max_rounds,
                    max_actions=detail.max_actions,
                ),
                detected_domains=(
                    detail.detected_domains
                ),
                initial_analysis_summary=(
                    analysis.summary
                ),
                initial_analysis_issues=tuple(
                    analysis.issues or []
                ),
                allowed_specialist_slugs=tuple(
                    selected_slugs
                ),
                investigation_actions_used=(
                    investigation_actions_used
                ),
            )
        )

        return ProjectToolResult(
            tool_id="run_specialist",
            success=True,
            data={
                "task": serialize_value(task),
                "specialist": (
                    serialize_specialist_definition(
                        specialist
                    )
                ),
                "result": (
                    serialize_specialist_loop_result(
                        result
                    )
                ),
            },
        )

    def _specialist_by_slug(
        self,
        arguments: dict[str, Any],
    ):
        self._require_dependency(
            self._specialist_registry,
            "specialist_registry",
        )

        slug = arguments.get(
            "specialist_slug"
        )
        if not isinstance(slug, str) or not slug.strip():
            raise ValueError(
                "specialist_slug must be a non-empty string."
            )

        return (
            self._specialist_registry
            .snapshot()
            .get_by_slug(slug)
        )

    async def _propose_remediation(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._remediation_service,
            "remediation_service",
        )

        proposal = (
            self._remediation_service
            .propose_remediation(
                investigation_id=self._required_string(
                    arguments,
                    "investigation_id",
                ),
                problem_summary=self._required_string(
                    arguments,
                    "problem_summary",
                ),
                diagnosis_claim_ids=(
                    self._required_string_list(
                        arguments,
                        "diagnosis_claim_ids",
                    )
                ),
                evidence_ids=self._required_string_list(
                    arguments,
                    "evidence_ids",
                ),
            )
        )

        return ProjectToolResult(
            tool_id="propose_remediation",
            success=True,
            data={
                "proposal": serialize_value(
                    proposal
                )
            },
        )

    async def _create_remediation_plan(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._remediation_service,
            "remediation_service",
        )

        actions = arguments.get(
            "proposed_actions"
        )
        if not isinstance(actions, list):
            raise ValueError(
                "proposed_actions must be a list."
            )

        plan = (
            self._remediation_service
            .create_plan(
                investigation_id=self._required_string(
                    arguments,
                    "investigation_id",
                ),
                title=self._required_string(
                    arguments,
                    "title",
                ),
                problem_summary=self._required_string(
                    arguments,
                    "problem_summary",
                ),
                proposed_actions=actions,
                diagnosis_claim_ids=(
                    self._required_string_list(
                        arguments,
                        "diagnosis_claim_ids",
                    )
                ),
                evidence_ids=self._required_string_list(
                    arguments,
                    "evidence_ids",
                ),
                risk_level=str(
                    arguments.get(
                        "risk_level",
                        "medium",
                    )
                ),
                rollback_plan=arguments.get(
                    "rollback_plan"
                ),
                plan_id=arguments.get("plan_id"),
            )
        )

        return ProjectToolResult(
            tool_id="create_remediation_plan",
            success=True,
            data={
                "plan": serialize_value(plan)
            },
        )

    async def _test_remediation_in_sandbox(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._remediation_service,
            "remediation_service",
        )
        result = (
            self._remediation_service
            .test_in_sandbox(
                plan_id=self._required_string(
                    arguments,
                    "plan_id",
                )
            )
        )

        return ProjectToolResult(
            tool_id="test_remediation_in_sandbox",
            success=True,
            data={
                "sandbox_result": serialize_value(
                    result
                )
            },
        )

    async def _get_sandbox_result(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._remediation_service,
            "remediation_service",
        )

        result_id = arguments.get("result_id")
        plan_id = arguments.get("plan_id")
        if result_id is not None and not isinstance(
            result_id,
            str,
        ):
            raise ValueError(
                "result_id must be a string."
            )
        if plan_id is not None and not isinstance(
            plan_id,
            str,
        ):
            raise ValueError(
                "plan_id must be a string."
            )

        result = (
            self._remediation_service
            .get_sandbox_result(
                result_id,
                plan_id=plan_id,
            )
        )
        if result is None:
            return ProjectToolResult(
                tool_id="get_sandbox_result",
                success=False,
                error_code="sandbox_result_not_found",
                error_message=(
                    "Sandbox result was not found."
                ),
            )

        return ProjectToolResult(
            tool_id="get_sandbox_result",
            success=True,
            data={
                "sandbox_result": serialize_value(
                    result
                )
            },
        )

    async def _request_user_approval(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._remediation_service,
            "remediation_service",
        )
        plan = (
            self._remediation_service
            .request_approval(
                plan_id=self._required_string(
                    arguments,
                    "plan_id",
                )
            )
        )

        return ProjectToolResult(
            tool_id="request_user_approval",
            success=True,
            data={
                "plan": serialize_value(plan),
                "approval_required": True,
            },
        )

    async def _apply_approved_remediation(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        self._require_dependency(
            self._remediation_service,
            "remediation_service",
        )
        outcome = (
            self._remediation_service
            .apply_approved(
                plan_id=self._required_string(
                    arguments,
                    "plan_id",
                ),
                approved_by=arguments.get(
                    "approved_by"
                ),
            )
        )

        return ProjectToolResult(
            tool_id="apply_approved_remediation",
            success=bool(
                outcome.get("applied")
            ),
            data={
                "outcome": serialize_value(
                    outcome
                )
            },
            error_code=(
                None
                if outcome.get("applied")
                else str(
                    outcome.get(
                        "blocked_reason",
                        "remediation_blocked",
                    )
                )
            ),
            error_message=(
                None
                if outcome.get("applied")
                else str(
                    outcome.get(
                        "message",
                        "Remediation was blocked.",
                    )
                )
            ),
        )

    def _read_investigation(
        self,
        arguments: dict[str, Any],
    ):
        self._require_dependency(
            self._investigation_read_service,
            "investigation_read_service",
        )

        investigation_id = arguments.get(
            "investigation_id"
        )
        if (
            not isinstance(investigation_id, str)
            or not investigation_id.strip()
        ):
            raise ValueError(
                "investigation_id must be a non-empty string."
            )

        return self._investigation_read_service.get(
            investigation_id.strip()
        )

    def _latest_report_for_server(
        self,
        server_id: int,
    ):
        items, total = (
            self._report_query_service
            .list_reports(
                server_id=server_id,
                page=1,
                page_size=1,
            )
        )

        if total < 1 or not items:
            return None

        return (
            self._report_query_service
            .get_report(
                items[0].id
            )
        )

    @staticmethod
    def _required_int(
        arguments: dict[str, Any],
        name: str,
    ) -> int:
        value = arguments.get(
            name
        )

        if not isinstance(value, int):
            raise ValueError(
                f"{name} must be an integer."
            )

        if value < 1:
            raise ValueError(
                f"{name} must be >= 1."
            )

        return value

    @staticmethod
    def _required_string(
        arguments: dict[str, Any],
        name: str,
    ) -> str:
        value = arguments.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{name} must be a non-empty string."
            )
        return value.strip()

    @staticmethod
    def _required_string_list(
        arguments: dict[str, Any],
        name: str,
    ) -> list[str]:
        value = arguments.get(name)
        if not isinstance(value, list) or not value:
            raise ValueError(
                f"{name} must be a non-empty list."
            )
        result: list[str] = []
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise ValueError(
                    f"{name} must contain strings."
                )
            result.append(item.strip())
        return result

    @staticmethod
    def _optional_int(
        arguments: dict[str, Any],
        name: str,
        *,
        default: int,
    ) -> int:
        value = arguments.get(
            name,
            default,
        )

        if not isinstance(value, int):
            raise ValueError(
                f"{name} must be an integer."
            )

        if value < 1:
            raise ValueError(
                f"{name} must be >= 1."
            )

        return value

    @staticmethod
    def _require_dependency(
        dependency,
        name: str,
    ) -> None:
        if dependency is None:
            raise ValueError(
                f"{name} is not configured."
            )

    @staticmethod
    def _build_definitions() -> list[
        ProjectToolDefinition
    ]:
        integer_id = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

        return [
            ProjectToolDefinition(
                tool_id="get_server_context",
                description=(
                    "Read server context through "
                    "project services."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "server_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["server_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_monitoring_profile",
                description=(
                    "Read monitoring profile and "
                    "assigned commands."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "profile_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["profile_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="run_monitoring",
                description=(
                    "Run existing project-owned "
                    "monitoring for a server."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "server_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["server_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_report",
                description=(
                    "Read a persisted monitoring "
                    "report."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["report_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_latest_report",
                description=(
                    "Read the latest persisted report "
                    "for a server."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "server_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["server_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="find_exact_report_match",
                description=(
                    "Find a completed analysis with "
                    "the same report fingerprint."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        }
                    },
                    "required": ["report_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="search_similar_incidents",
                description=(
                    "Search historical incident RAG "
                    "for similar reports."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3,
                        },
                    },
                    "required": ["report_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_top_similar_reports",
                description=(
                    "Return at most the top 3 similar "
                    "historical reports."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 3,
                        },
                    },
                    "required": ["report_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="analyze_report",
                description=(
                    "Analyze a report through the "
                    "existing AnalysisOrchestrator."
                ),
                input_schema={
                    **integer_id,
                    "properties": {
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "force": {
                            "type": "boolean",
                        },
                    },
                    "required": ["report_id"],
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_analysis",
                description=(
                    "Read persisted report analysis by "
                    "analysis_id or report_id."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "analysis_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                    },
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="search_knowledge",
                description=(
                    "Search project-owned Knowledge RAG."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                        },
                        "specialist_slug": {
                            "type": "string",
                        },
                        "domains": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 6,
                        },
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="start_investigation",
                description=(
                    "Persist an investigation routing "
                    "decision for a report and analysis."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "report_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                        "analysis_id": {
                            "type": "integer",
                            "minimum": 1,
                        },
                    },
                    "required": ["report_id"],
                    "additionalProperties": False,
                },
                read_only=False,
            ),
            ProjectToolDefinition(
                tool_id="get_investigation",
                description=(
                    "Read a persisted investigation "
                    "detail model."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "investigation_id": {
                            "type": "string",
                        }
                    },
                    "required": ["investigation_id"],
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_investigation_status",
                description=(
                    "Read investigation status and "
                    "selected Specialists."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "investigation_id": {
                            "type": "string",
                        }
                    },
                    "required": ["investigation_id"],
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_evidence",
                description=(
                    "Read persisted runtime Evidence "
                    "for an investigation."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "investigation_id": {
                            "type": "string",
                        }
                    },
                    "required": ["investigation_id"],
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_available_specialists",
                description=(
                    "Read enabled Specialist runtime "
                    "definitions from the DB-backed "
                    "registry."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "domains": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        }
                    },
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="get_specialist_definition",
                description=(
                    "Read one enabled Specialist "
                    "runtime definition by slug."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "specialist_slug": {
                            "type": "string",
                        }
                    },
                    "required": ["specialist_slug"],
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="run_specialist",
                description=(
                    "Run a selected Specialist through "
                    "the existing Ollama-backed "
                    "specialist investigation loop."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "investigation_id": {
                            "type": "string",
                        },
                        "specialist_slug": {
                            "type": "string",
                        },
                        "objective": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "investigation_id",
                        "specialist_slug",
                        "objective",
                    ],
                    "additionalProperties": False,
                },
                read_only=False,
            ),
            ProjectToolDefinition(
                tool_id="propose_remediation",
                description=(
                    "Create a grounded remediation "
                    "proposal linked to diagnosis "
                    "claims and Evidence."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "investigation_id": {
                            "type": "string",
                        },
                        "problem_summary": {
                            "type": "string",
                        },
                        "diagnosis_claim_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "evidence_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                    },
                    "required": [
                        "investigation_id",
                        "problem_summary",
                        "diagnosis_claim_ids",
                        "evidence_ids",
                    ],
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="create_remediation_plan",
                description=(
                    "Persist an auditable remediation "
                    "plan before sandbox validation."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                        },
                        "investigation_id": {
                            "type": "string",
                        },
                        "title": {
                            "type": "string",
                        },
                        "problem_summary": {
                            "type": "string",
                        },
                        "proposed_actions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                            },
                        },
                        "diagnosis_claim_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "evidence_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                        "risk_level": {
                            "type": "string",
                        },
                        "rollback_plan": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "investigation_id",
                        "title",
                        "problem_summary",
                        "proposed_actions",
                        "diagnosis_claim_ids",
                        "evidence_ids",
                    ],
                    "additionalProperties": False,
                },
                read_only=False,
            ),
            ProjectToolDefinition(
                tool_id="test_remediation_in_sandbox",
                description=(
                    "Validate a remediation plan in an "
                    "isolated sandbox dry-run."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                        }
                    },
                    "required": ["plan_id"],
                    "additionalProperties": False,
                },
                read_only=False,
            ),
            ProjectToolDefinition(
                tool_id="get_sandbox_result",
                description=(
                    "Read an auditable sandbox result "
                    "by result_id or plan_id."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "result_id": {
                            "type": "string",
                        },
                        "plan_id": {
                            "type": "string",
                        },
                    },
                    "additionalProperties": False,
                },
                read_only=True,
            ),
            ProjectToolDefinition(
                tool_id="request_user_approval",
                description=(
                    "Record that a remediation plan "
                    "requires explicit user approval."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                        }
                    },
                    "required": ["plan_id"],
                    "additionalProperties": False,
                },
                read_only=False,
            ),
            ProjectToolDefinition(
                tool_id="apply_approved_remediation",
                description=(
                    "Attempt production application "
                    "only after sandbox and policy "
                    "authorization."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                        },
                        "approved_by": {
                            "type": "string",
                        },
                    },
                    "required": ["plan_id"],
                    "additionalProperties": False,
                },
                read_only=False,
            ),
        ]
