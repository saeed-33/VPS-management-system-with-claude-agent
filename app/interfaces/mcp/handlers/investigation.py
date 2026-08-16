"""
حد MCP يكشف Project capabilities لـClaude عبر أدوات typed ومتحقق منها.

الموقع في المعمارية: MCP capability boundary.
يُستدعى بواسطة: Claude أو خادم MCP.
يعتمد مباشرة على: app.core.contracts.investigation، app.interfaces.mcp.schemas، app.interfaces.mcp.serializers.
الحد المعماري: MCP exposure ليس enforcement أمنيًا مستقلًا؛ التحقق الفعلي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from typing import Any

from app.core.contracts.investigation import (
    InvestigationBudget,
    SpecialistTask,
    SpecialistTaskStatus,
)
from app.interfaces.mcp.schemas import ProjectToolResult
from app.interfaces.mcp.serializers import (
    serialize_specialist_definition,
    serialize_specialist_loop_result,
    serialize_value,
)


class InvestigationToolsMixin:
    """
    يمثل InvestigationToolsMixin مسؤولية محددة داخل طبقة MCP capability boundary.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Claude أو خادم MCP
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    async def _start_investigation(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _start_investigation؛ المدخلات المهمة: arguments.
        تعيد ProjectToolResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _get_investigation؛ المدخلات المهمة: arguments.
        تعيد ProjectToolResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _get_investigation_status؛ المدخلات المهمة: arguments.
        تعيد ProjectToolResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
                **self._specialist_progress(detail),
            },
        )

    async def _get_evidence(
        self,
        arguments: dict[str, Any],
    ) -> ProjectToolResult:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _get_evidence؛ المدخلات المهمة: arguments.
        تعيد ProjectToolResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _get_available_specialists؛ المدخلات المهمة: arguments.
        تعيد ProjectToolResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _get_specialist_definition؛ المدخلات المهمة: arguments.
        تعيد ProjectToolResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _run_specialist؛ المدخلات المهمة: arguments.
        تعيد ProjectToolResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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

        execution_service = getattr(
            self,
            "_specialist_execution_service",
            None,
        )
        ownership_token = None
        if execution_service is not None:
            reservation = execution_service.reserve_with_token(
                investigation_id=detail.investigation_id,
                specialist_slug=specialist.slug,
            )
            if reservation["status"] == "completed":
                return ProjectToolResult(
                    tool_id="run_specialist",
                    success=True,
                    data={
                        "specialist": serialize_specialist_definition(specialist),
                        "result": reservation.get("run"),
                        "persisted": True,
                        "idempotent": True,
                        "runtime": self._specialist_progress(detail),
                    },
                )
            if reservation["status"] == "in_progress":
                return ProjectToolResult(
                    tool_id="run_specialist",
                    success=False,
                    error_code="specialist_in_progress",
                    error_message=(
                        "This Specialist is already reserved by another "
                        "worker; read persisted investigation status and retry "
                        "only if the lease expires."
                    ),
                )
            ownership_token = reservation["ownership_token"]
            investigation_actions_used = int(reservation.get("actions_used") or 0)

        if execution_service is None and detail.runtime is not None:
            investigation_actions_used = (
                detail.runtime.actions_used or 0
            )
        elif execution_service is None:
            investigation_actions_used = 0

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

        try:
            result = await (
                self._specialist_investigation_loop.run(
                    task=task,
                    specialist=specialist,
                    investigation_budget=InvestigationBudget(
                        max_specialists=detail.max_specialists,
                        max_rounds=detail.max_rounds,
                        max_actions=detail.max_actions,
                    ),
                    detected_domains=detail.detected_domains,
                    initial_analysis_summary=analysis.summary,
                    initial_analysis_issues=tuple(analysis.issues or []),
                    allowed_specialist_slugs=tuple(selected_slugs),
                    investigation_actions_used=investigation_actions_used,
                )
            )
        except Exception as exc:
            if execution_service is None or ownership_token is None:
                raise
            persisted = await execution_service.finalize_failure(
                task=task,
                reason=str(exc),
                selected_specialists=tuple(selected_slugs),
                ownership_token=ownership_token,
            )
            return ProjectToolResult(
                tool_id="run_specialist",
                success=False,
                data={"result": persisted["run"], "runtime": persisted["snapshot"]},
                error_code="specialist_execution_failed",
                error_message=str(exc),
            )

        persisted = None
        if execution_service is not None and ownership_token is not None:
            persisted = await execution_service.finalize(
                task=task,
                loop_result=result,
                selected_specialists=tuple(selected_slugs),
                ownership_token=ownership_token,
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
                "persisted_result": (
                    persisted["run"]
                    if persisted is not None
                    else None
                ),
                "runtime": (
                    persisted["snapshot"]
                    if persisted is not None
                    else None
                ),
            },
        )

    def _specialist_progress(self, detail):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _specialist_progress؛ المدخلات المهمة: detail.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        selected = [
            candidate.specialist_slug
            for candidate in detail.candidates
            if candidate.is_selected
        ]
        metadata = (
            detail.runtime.metadata or {}
            if detail.runtime is not None
            else {}
        )
        completed = list(metadata.get("completed_specialists", ()))
        failed = list(metadata.get("failed_specialists", ()))
        terminal = set(completed) | set(failed)
        return {
            "selected_specialists": list(metadata.get("selected_specialists", selected)),
            "completed_specialists": completed,
            "failed_specialists": failed,
            "remaining_specialists": list(
                metadata.get(
                    "remaining_specialists",
                    [slug for slug in selected if slug not in terminal],
                )
            ),
            "runtime_available": bool(detail.runtime_available),
            "final_diagnosis_available": bool(detail.final_diagnosis_available),
            "status": detail.status,
        }

    def _specialist_by_slug(
        self,
        arguments: dict[str, Any],
    ):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _specialist_by_slug؛ المدخلات المهمة: arguments.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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

    def _read_investigation(
        self,
        arguments: dict[str, Any],
    ):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _read_investigation؛ المدخلات المهمة: arguments.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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
