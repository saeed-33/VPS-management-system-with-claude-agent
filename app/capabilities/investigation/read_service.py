"""
قراءة التحقيقات وملخصاتها وتفاصيلها.

تجمع الخدمة البيانات المحفوظة من سجلات التحقيق والتشغيل والمرشحين والأدلة
وتعرضها في نماذج قراءة مناسبة للواجهات.
"""
from __future__ import annotations

from app.core.ports.investigation.investigation_repository import InvestigationRepositoryPort
from app.core.contracts.investigation_read_models.investigation_candidate_read_model import InvestigationCandidateReadModel
from app.core.contracts.investigation_read_models.investigation_detail_read_model import InvestigationDetailReadModel
from app.core.contracts.investigation_read_models.investigation_runtime_read_model import InvestigationRuntimeReadModel
from app.core.contracts.investigation_read_models.investigation_summary_read_model import InvestigationSummaryReadModel


class InvestigationReadService:
    """
    يحوّل سجلات التحقيق إلى ملخصات وتفاصيل للقراءة.
    """
    def __init__(
        self,
        repository: InvestigationRepositoryPort,
    ) -> None:
        """
        يهيئ InvestigationReadService ويربط الاعتماديات اللازمة لدورة التحقيق.
        """
        self._repository = repository

    def get(
        self,
        investigation_id: str,
    ) -> InvestigationDetailReadModel | None:
        """
        يجلب تحقيقًا ويحوّله إلى تفاصيل قراءة.
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
        يعرض أحدث التحقيقات وفق حدود القراءة.
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
        يعرض التحقيقات المرتبطة بتقرير مراقبة.
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
        يبني ملخص قراءة من سجل التحقيق.
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
        يبني تفاصيل قراءة موسعة مع الأدلة والتشغيل.
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
        يحوّل مرشح التحقيق إلى عقد قراءة.
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
        يحوّل حالة التشغيل إلى عقد قراءة.
        """
        def dict_tuple(value):
            """
            يحوّل قيمة قائمة أو tuple من القواميس إلى tuple مستقرة لعرض حالة التشغيل.
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
            يحوّل القيمة الرقمية الاختيارية إلى عدد صحيح أو يعيد قيمة فارغة.
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
