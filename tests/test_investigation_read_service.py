from datetime import datetime, timezone

from app.shared.services.investigation_read_service import (
    InvestigationReadService,
)


class Candidate:
    specialist_definition_id = 10
    specialist_slug = "nginx"
    specialist_name = "NGINX Specialist"
    score = 5
    priority = 100
    candidate_rank = 1
    is_selected = True
    selected_rank = 1
    matched_domains = ["nginx", "http"]
    matched_trigger_hints = []
    matched_issue_indexes = [0]


class Model:
    investigation_id = "inv-1"
    server_id = 2
    report_id = 1076
    analysis_id = 907
    status = "completed"
    should_investigate = True
    routing_reasons = ["actionable_issue"]
    detected_domains = ["nginx"]
    unmatched_issue_indexes = []
    registry_size = 8
    candidate_limit = 12
    selection_limit = 4
    max_specialists = 4
    max_rounds = 3
    max_actions = 12
    routing_version = "deterministic-v1"
    candidates = [Candidate()]
    created_at = datetime(
        2026,
        8,
        10,
        tzinfo=timezone.utc,
    )
    updated_at = created_at
    investigation_metadata = {}


class Repository:
    def __init__(self, model):
        self.model = model

    def get_by_investigation_id(
        self,
        investigation_id,
    ):
        if (
            investigation_id
            == self.model.investigation_id
        ):
            return self.model
        return None

    def list_recent(
        self,
        *,
        limit,
        server_id=None,
    ):
        return [self.model]

    def list_by_report_id(
        self,
        report_id,
    ):
        if report_id == self.model.report_id:
            return [self.model]
        return []


def test_read_model_does_not_invent_runtime():
    model = Model()
    model.investigation_metadata = {}

    output = InvestigationReadService(
        Repository(model)
    ).get("inv-1")

    assert output is not None
    assert output.runtime_available is False
    assert (
        output.final_diagnosis_available
        is False
    )
    assert output.runtime is None


def test_runtime_snapshot_is_exposed_when_persisted():
    model = Model()
    model.investigation_metadata = {
        "runtime_snapshot": {
            "status": "completed",
            "orchestrator": "langgraph",
            "execution_mode": (
                "dynamic-secondary"
            ),
            "waves_completed": 2,
            "actions_used": 4,
            "evidence_count": 7,
            "specialist_runs": [
                {
                    "specialist_slug": (
                        "nginx"
                    ),
                    "status": "completed",
                }
            ],
            "evidence": [
                {
                    "evidence_id": "e1"
                }
            ],
            "correlated_claims": [
                {
                    "claim_id": "c1",
                    "certainty": (
                        "confirmed"
                    ),
                }
            ],
            "conflicts": [],
            "final_diagnosis": {
                "summary": "Stable."
            },
            "narrative": {
                "summary": "Stable."
            },
        }
    }

    output = InvestigationReadService(
        Repository(model)
    ).get("inv-1")

    assert output is not None
    assert output.runtime_available is True
    assert (
        output.final_diagnosis_available
        is True
    )
    assert output.runtime is not None
    assert (
        output.runtime.orchestrator
        == "langgraph"
    )
    assert (
        output.runtime.execution_mode
        == "dynamic-secondary"
    )


def test_summary_exposes_selected_specialists():
    model = Model()
    model.investigation_metadata = {}

    output = InvestigationReadService(
        Repository(model)
    ).list_recent(
        limit=25,
        server_id=2,
    )

    assert len(output) == 1
    assert (
        output[0].selected_specialists
        == ("nginx",)
    )


def test_list_limit_is_bounded():
    service = InvestigationReadService(
        Repository(Model())
    )

    for value in (0, 501):
        try:
            service.list_recent(
                limit=value
            )
        except ValueError as exc:
            assert "between 1 and 500" in (
                str(exc)
            )
        else:
            raise AssertionError(
                "Invalid list limit accepted."
            )
