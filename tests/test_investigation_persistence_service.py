from app.domain.investigation.contracts import InvestigationBudget
from app.domain.investigation.investigation_router import (
    InvestigationRoutingDecision,
    RoutingReason,
    SpecialistRoutingMatch,
)
from app.domain.investigation.persistence_service import (
    InvestigationPersistenceService,
)


class FakeRepository:
    def __init__(self):
        self.created = None

    def create(self, data):
        self.created = data
        return data

    def get_by_investigation_id(self, investigation_id):
        return None


def make_match(i, slug, score, priority):
    return SpecialistRoutingMatch(
        specialist_id=i,
        specialist_slug=slug,
        specialist_name=slug,
        score=score,
        matched_domains=(slug,),
        matched_trigger_hints=(),
        matched_issue_indexes=(0,),
        priority=priority,
    )


def test_persistence_preserves_candidate_and_selected_ranks():
    repository = FakeRepository()
    service = InvestigationPersistenceService(repository)

    first = make_match(1, "linux-network", 9, 25)
    second = make_match(2, "linux-process", 2, 30)

    decision = InvestigationRoutingDecision(
        should_investigate=True,
        reasons=(
            RoutingReason.ANALYSIS_ISSUES,
            RoutingReason.REPORT_FAILURE,
        ),
        detected_domains=("network",),
        candidate_specialists=(first, second),
        selected_specialists=(first,),
        unmatched_issue_indexes=(),
        registry_size=9,
        candidate_limit=12,
        selection_limit=4,
    )

    created = service.persist_routing_decision(
        server_id=2,
        report_id=807,
        analysis_id=638,
        decision=decision,
        budget=InvestigationBudget(
            max_specialists=4,
            max_rounds=3,
            max_actions=12,
        ),
    )

    assert created is repository.created
    assert len(created.candidates) == 2
    assert created.candidates[0].candidate_rank == 1
    assert created.candidates[0].is_selected is True
    assert created.candidates[0].selected_rank == 1
    assert created.candidates[1].candidate_rank == 2
    assert created.candidates[1].is_selected is False
    assert created.candidates[1].selected_rank is None


def test_healthy_decision_can_be_persisted_for_audit():
    repository = FakeRepository()
    service = InvestigationPersistenceService(repository)

    decision = InvestigationRoutingDecision(
        should_investigate=False,
        reasons=(RoutingReason.NO_ACTIONABLE_SIGNAL,),
        detected_domains=(),
        candidate_specialists=(),
        selected_specialists=(),
        unmatched_issue_indexes=(),
        registry_size=9,
        candidate_limit=12,
        selection_limit=4,
    )

    created = service.persist_routing_decision(
        server_id=1,
        report_id=825,
        analysis_id=656,
        decision=decision,
    )

    assert created.should_investigate is False
    assert created.candidates == ()
    assert created.metadata["candidate_count"] == 0
    assert created.metadata["selected_count"] == 0
