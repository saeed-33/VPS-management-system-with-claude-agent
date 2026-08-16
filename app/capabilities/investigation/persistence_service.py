"""
حفظ قرار توجيه التحقيق وقراءته.

يربط قرار التوجيه بالتقرير والسيرفر ويحوّل سجل التخزين إلى عقد قراءة دون
تكرار منطق التوجيه داخل الواجهة.
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
    يحفظ قرار توجيه التحقيق ويقرأه من المستودع.
    """
    def __init__(self, repository: InvestigationRepository) -> None:
        """
        يهيئ InvestigationPersistenceService ويربط الاعتماديات اللازمة لدورة التحقيق.
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
        يحفظ قرار التوجيه والمرشحين المرتبطين بتقرير التحقيق.
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
        يقرأ قرار توجيه محفوظًا ويعيده بصيغة العقد.
        """
        return self._repository.get_by_investigation_id(investigation_id)
