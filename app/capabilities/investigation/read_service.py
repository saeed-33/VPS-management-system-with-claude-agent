"""
جزء من Investigation/Specialist لتوجيه التحقيق وجمع Evidence وبناء التشخيص.

الموقع في المعمارية: Application capability / investigation.
يُستدعى بواسطة: MCP أو Analysis workflow.
يعتمد مباشرة على: app.infrastructure.database.repositories.investigation_repository، app.core.contracts.investigation_read_models.
الحد المعماري: لا يتجاوز Diagnostic Policy؛ Python يتحقق وينفذ collection.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from app.infrastructure.database.repositories.investigation_repository import (
    InvestigationRepository,
)
from app.core.contracts.investigation_read_models import (
    InvestigationCandidateReadModel,
    InvestigationDetailReadModel,
    InvestigationRuntimeReadModel,
    InvestigationSummaryReadModel,
)


class InvestigationReadService:
    """
    يمثل InvestigationReadService مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
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

    def get(
        self,
        investigation_id: str,
    ) -> InvestigationDetailReadModel | None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى get؛ المدخلات المهمة: investigation_id.
        تعيد InvestigationDetailReadModel | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        model = self._repository.get_by_investigation_id(
            investigation_id
        )
        if model is None:
            return None
        return self._detail(model)

    def list_recent(
        self,
        *,
        limit: int = 100,
        server_id: int | None = None,
    ) -> tuple[InvestigationSummaryReadModel, ...]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى list_recent؛ المدخلات المهمة: limit، server_id.
        تعيد tuple[InvestigationSummaryReadModel, ...] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if limit < 1 or limit > 500:
            raise ValueError(
                "limit must be between 1 and 500."
            )

        models = self._repository.list_recent(
            limit=limit,
            server_id=server_id,
        )
        return tuple(
            self._summary(model)
            for model in models
        )

    def list_by_report_id(
        self,
        report_id: int,
    ) -> tuple[InvestigationSummaryReadModel, ...]:
        """
        يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى list_by_report_id؛ المدخلات المهمة: report_id.
        تعيد tuple[InvestigationSummaryReadModel, ...] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if report_id < 1:
            raise ValueError(
                "report_id must be >= 1."
            )
        return tuple(
            self._summary(model)
            for model
            in self._repository.list_by_report_id(
                report_id
            )
        )

    def _summary(
        self,
        model,
    ) -> InvestigationSummaryReadModel:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _summary؛ المدخلات المهمة: model.
        تعيد InvestigationSummaryReadModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        metadata = dict(
            model.investigation_metadata or {}
        )
        runtime = metadata.get(
            "runtime_snapshot"
        )
        runtime_available = (
            isinstance(runtime, dict)
            and bool(runtime.get("runtime_available", True))
        )
        final_available = (
            runtime_available
            and isinstance(
                runtime.get(
                    "final_diagnosis"
                ),
                dict,
            )
        )
        selected = tuple(
            candidate.specialist_slug
            for candidate in model.candidates
            if candidate.is_selected
        )

        return InvestigationSummaryReadModel(
            investigation_id=model.investigation_id,
            server_id=model.server_id,
            report_id=model.report_id,
            analysis_id=model.analysis_id,
            status=model.status,
            should_investigate=model.should_investigate,
            detected_domains=tuple(
                model.detected_domains or ()
            ),
            selected_specialists=selected,
            max_specialists=model.max_specialists,
            max_rounds=model.max_rounds,
            max_actions=model.max_actions,
            runtime_available=runtime_available,
            final_diagnosis_available=final_available,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _detail(
        self,
        model,
    ) -> InvestigationDetailReadModel:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _detail؛ المدخلات المهمة: model.
        تعيد InvestigationDetailReadModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        metadata = dict(
            model.investigation_metadata or {}
        )
        raw_runtime = metadata.get(
            "runtime_snapshot"
        )
        raw_runtime_available = (
            isinstance(raw_runtime, dict)
            and bool(raw_runtime.get("runtime_available", True))
        )
        runtime = (
            self._runtime(raw_runtime)
            if isinstance(raw_runtime, dict)
            else None
        )

        return InvestigationDetailReadModel(
            investigation_id=model.investigation_id,
            server_id=model.server_id,
            report_id=model.report_id,
            analysis_id=model.analysis_id,
            status=model.status,
            should_investigate=model.should_investigate,
            routing_reasons=tuple(
                model.routing_reasons or ()
            ),
            detected_domains=tuple(
                model.detected_domains or ()
            ),
            unmatched_issue_indexes=tuple(
                model.unmatched_issue_indexes
                or ()
            ),
            registry_size=model.registry_size,
            candidate_limit=model.candidate_limit,
            selection_limit=model.selection_limit,
            max_specialists=model.max_specialists,
            max_rounds=model.max_rounds,
            max_actions=model.max_actions,
            routing_version=model.routing_version,
            candidates=tuple(
                self._candidate(candidate)
                for candidate
                in model.candidates
            ),
            runtime_available=(
                raw_runtime_available
                and runtime is not None
            ),
            final_diagnosis_available=(
                raw_runtime_available
                and runtime is not None
                and runtime.final_diagnosis
                is not None
            ),
            runtime=runtime,
            metadata=metadata,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _candidate(
        self,
        model,
    ) -> InvestigationCandidateReadModel:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _candidate؛ المدخلات المهمة: model.
        تعيد InvestigationCandidateReadModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return InvestigationCandidateReadModel(
            specialist_definition_id=(
                model.specialist_definition_id
            ),
            specialist_slug=model.specialist_slug,
            specialist_name=model.specialist_name,
            score=model.score,
            priority=model.priority,
            candidate_rank=model.candidate_rank,
            is_selected=model.is_selected,
            selected_rank=model.selected_rank,
            matched_domains=tuple(
                model.matched_domains or ()
            ),
            matched_trigger_hints=tuple(
                model.matched_trigger_hints or ()
            ),
            matched_issue_indexes=tuple(
                model.matched_issue_indexes or ()
            ),
        )

    def _runtime(
        self,
        raw: dict,
    ) -> InvestigationRuntimeReadModel:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى _runtime؛ المدخلات المهمة: raw.
        تعيد InvestigationRuntimeReadModel أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        def dict_tuple(value):
            """
            ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

            تُستدعى عندما يصل workflow إلى dict_tuple؛ المدخلات المهمة: value.
            تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
            قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
            """
            if not isinstance(
                value,
                (list, tuple),
            ):
                return ()
            return tuple(
                dict(item)
                for item in value
                if isinstance(item, dict)
            )

        def optional_int(value):
            """
            ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

            تُستدعى عندما يصل workflow إلى optional_int؛ المدخلات المهمة: value.
            تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
            قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
            """
            if value is None:
                return None
            try:
                return int(value)
            except (
                TypeError,
                ValueError,
            ):
                return None

        return InvestigationRuntimeReadModel(
            status=(
                str(raw["status"])
                if raw.get("status")
                is not None
                else None
            ),
            orchestrator=(
                str(raw["orchestrator"])
                if raw.get("orchestrator")
                is not None
                else None
            ),
            execution_mode=(
                str(raw["execution_mode"])
                if raw.get(
                    "execution_mode"
                )
                is not None
                else None
            ),
            waves_completed=optional_int(
                raw.get(
                    "waves_completed"
                )
            ),
            actions_used=optional_int(
                raw.get("actions_used")
            ),
            evidence_count=optional_int(
                raw.get("evidence_count")
            ),
            specialist_runs=dict_tuple(
                raw.get("specialist_runs")
            ),
            evidence=dict_tuple(
                raw.get("evidence")
            ),
            correlated_claims=dict_tuple(
                raw.get(
                    "correlated_claims"
                )
            ),
            conflicts=dict_tuple(
                raw.get("conflicts")
            ),
            final_diagnosis=(
                dict(
                    raw["final_diagnosis"]
                )
                if isinstance(
                    raw.get(
                        "final_diagnosis"
                    ),
                    dict,
                )
                else None
            ),
            narrative=(
                dict(raw["narrative"])
                if isinstance(
                    raw.get("narrative"),
                    dict,
                )
                else None
            ),
            metadata=(
                dict(raw["metadata"])
                if isinstance(
                    raw.get("metadata"),
                    dict,
                )
                else {}
            ),
        )
