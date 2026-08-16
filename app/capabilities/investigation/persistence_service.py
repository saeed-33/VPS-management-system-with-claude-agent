"""
جزء من Investigation/Specialist لتوجيه التحقيق وجمع Evidence وبناء التشخيص.

الموقع في المعمارية: Application capability / investigation.
يُستدعى بواسطة: MCP أو Analysis workflow.
يعتمد مباشرة على: app.core.contracts.investigation، app.capabilities.investigation.investigation_router، app.infrastructure.database.repositories.investigation_repository، app.core.contracts.investigations.
الحد المعماري: لا يتجاوز Diagnostic Policy؛ Python يتحقق وينفذ collection.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from uuid import uuid4

from app.core.contracts.investigation import InvestigationBudget
from app.capabilities.investigation.investigation_router import InvestigationRoutingDecision
from app.infrastructure.database.repositories.investigation_repository import InvestigationRepository
from app.core.contracts.investigations import (
    PersistInvestigationCandidateDTO,
    PersistInvestigationDTO,
)


class InvestigationPersistenceService:
    """
    يمثل InvestigationPersistenceService مسؤولية محددة داخل طبقة Application capability / investigation.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه MCP أو Analysis workflow
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, repository: InvestigationRepository) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: repository.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._repository = repository

    def persist_routing_decision(
        self,
        *,
        server_id: int,
        report_id: int,
        analysis_id: int | None,
        decision: InvestigationRoutingDecision,
        budget: InvestigationBudget | None = None,
        routing_version: str = "deterministic-v1",
    ):
        """
        ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى persist_routing_decision؛ المدخلات المهمة: server_id، report_id، analysis_id، decision، budget، routing_version.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        budget = budget or InvestigationBudget()

        selected_rank_by_slug = {
            item.specialist_slug: index
            for index, item in enumerate(decision.selected_specialists, start=1)
        }

        candidates = tuple(
            PersistInvestigationCandidateDTO(
                specialist_definition_id=item.specialist_id,
                specialist_slug=item.specialist_slug,
                specialist_name=item.specialist_name,
                score=item.score,
                priority=item.priority,
                candidate_rank=index,
                is_selected=item.specialist_slug in selected_rank_by_slug,
                selected_rank=selected_rank_by_slug.get(item.specialist_slug),
                matched_domains=item.matched_domains,
                matched_trigger_hints=item.matched_trigger_hints,
                matched_issue_indexes=item.matched_issue_indexes,
            )
            for index, item in enumerate(decision.candidate_specialists, start=1)
        )

        return self._repository.create(
            PersistInvestigationDTO(
                investigation_id=str(uuid4()),
                server_id=server_id,
                report_id=report_id,
                analysis_id=analysis_id,
                status="created",
                should_investigate=decision.should_investigate,
                routing_reasons=tuple(reason.value for reason in decision.reasons),
                detected_domains=decision.detected_domains,
                unmatched_issue_indexes=decision.unmatched_issue_indexes,
                registry_size=decision.registry_size,
                candidate_limit=decision.candidate_limit,
                selection_limit=decision.selection_limit,
                max_specialists=budget.max_specialists,
                max_rounds=budget.max_rounds,
                max_actions=budget.max_actions,
                routing_version=routing_version,
                candidates=candidates,
                metadata={
                    "candidate_count": len(decision.candidate_specialists),
                    "selected_count": len(decision.selected_specialists),
                },
            )
        )

    def get(self, investigation_id: str):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / investigation.

        تُستدعى عندما يصل workflow إلى get؛ المدخلات المهمة: investigation_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return self._repository.get_by_investigation_id(investigation_id)
