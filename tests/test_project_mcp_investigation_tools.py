import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

from app.capabilities.investigation.investigation_router import (
    InvestigationRoutingDecision,
    RoutingReason,
    SpecialistRoutingMatch,
)
from app.interfaces.mcp import (
    ProjectMcpToolBoundary,
    ProjectToolCall,
)
from app.core.contracts.investigation_read_models import (
    InvestigationCandidateReadModel,
    InvestigationDetailReadModel,
    InvestigationRuntimeReadModel,
)

from tests.test_project_mcp_analysis_tools import (
    Analysis,
    AnalysisRepository,
)
from tests.test_project_mcp_tool_boundary import (
    MonitoringService,
    ProfileService,
    ReportService,
    ServerService,
)


NOW = datetime(
    2026,
    8,
    11,
    tzinfo=timezone.utc,
)


class Router:
    def __init__(self):
        self.calls = []

    def route(
        self,
        *,
        report,
        analysis,
    ):
        self.calls.append(
            {
                "report_id": report.id,
                "analysis_id": analysis.id,
            }
        )
        match = SpecialistRoutingMatch(
            specialist_id=1,
            specialist_slug="linux-cpu",
            specialist_name="Linux CPU",
            score=10,
            matched_domains=("cpu",),
            matched_trigger_hints=("high cpu",),
            matched_issue_indexes=(0,),
            priority=10,
        )
        return InvestigationRoutingDecision(
            should_investigate=True,
            reasons=(
                RoutingReason.ANALYSIS_ISSUES,
            ),
            detected_domains=("cpu",),
            candidate_specialists=(match,),
            selected_specialists=(match,),
            unmatched_issue_indexes=(),
            registry_size=1,
            candidate_limit=12,
            selection_limit=4,
        )


@dataclass
class PersistedInvestigation:
    investigation_id: str


class PersistenceService:
    def __init__(self):
        self.calls = []

    def persist_routing_decision(
        self,
        **kwargs,
    ):
        self.calls.append(
            kwargs
        )
        return PersistedInvestigation(
            investigation_id="inv-1"
        )


class ReadService:
    def __init__(self):
        self.detail = InvestigationDetailReadModel(
            investigation_id="inv-1",
            server_id=1,
            report_id=10,
            analysis_id=4,
            status="created",
            should_investigate=True,
            routing_reasons=("analysis_issues",),
            detected_domains=("cpu",),
            unmatched_issue_indexes=(),
            registry_size=1,
            candidate_limit=12,
            selection_limit=4,
            max_specialists=4,
            max_rounds=3,
            max_actions=12,
            routing_version="deterministic-v1",
            candidates=(
                InvestigationCandidateReadModel(
                    specialist_definition_id=1,
                    specialist_slug="linux-cpu",
                    specialist_name="Linux CPU",
                    score=10,
                    priority=10,
                    candidate_rank=1,
                    is_selected=True,
                    selected_rank=1,
                ),
            ),
            runtime_available=True,
            final_diagnosis_available=False,
            runtime=InvestigationRuntimeReadModel(
                status="completed",
                evidence=(
                    {
                        "evidence_id": "ev-1",
                        "kind": "command_result",
                    },
                ),
            ),
            metadata={},
            created_at=NOW,
            updated_at=NOW,
        )

    def get(
        self,
        investigation_id,
    ):
        if investigation_id == "missing":
            return None
        return self.detail


class EmptyAnalysisRepository(AnalysisRepository):
    def get_by_report_id(
        self,
        report_id,
    ):
        return None


def boundary(
    *,
    analysis_repository=None,
    router=None,
    persistence=None,
    read=None,
):
    return ProjectMcpToolBoundary(
        server_service=ServerService(),
        monitoring_profile_service=(
            ProfileService()
        ),
        monitoring_service=MonitoringService(),
        report_query_service=ReportService(),
        analysis_repository=(
            analysis_repository
            if analysis_repository is not None
            else AnalysisRepository()
        ),
        investigation_router=(
            router
            if router is not None
            else Router()
        ),
        investigation_persistence_service=(
            persistence
            if persistence is not None
            else PersistenceService()
        ),
        investigation_read_service=(
            read
            if read is not None
            else ReadService()
        ),
    )


def run_tool(
    tool_id,
    arguments,
    *,
    tool_boundary=None,
):
    return asyncio.run(
        (
            tool_boundary
            if tool_boundary is not None
            else boundary()
        ).execute(
            ProjectToolCall(
                tool_id=tool_id,
                arguments=arguments,
            )
        )
    )


def test_start_investigation_routes_and_persists_decision():
    router = Router()
    persistence = PersistenceService()

    result = run_tool(
        "start_investigation",
        {
            "report_id": 10,
        },
        tool_boundary=boundary(
            router=router,
            persistence=persistence,
        ),
    )

    assert result.success is True
    assert (
        result.data["investigation"][
            "investigation_id"
        ]
        == "inv-1"
    )
    assert result.data["routing"][
        "selected_specialists"
    ] == ["linux-cpu"]
    assert router.calls == [
        {
            "report_id": 10,
            "analysis_id": 4,
        }
    ]
    assert persistence.calls[0]["server_id"] == 1
    assert persistence.calls[0]["analysis_id"] == 4


def test_start_investigation_requires_analysis():
    result = run_tool(
        "start_investigation",
        {
            "report_id": 10,
        },
        tool_boundary=boundary(
            analysis_repository=(
                EmptyAnalysisRepository()
            )
        ),
    )

    assert result.success is False
    assert result.error_code == "analysis_not_found"


def test_get_investigation_reads_detail():
    result = run_tool(
        "get_investigation",
        {
            "investigation_id": "inv-1",
        },
    )

    assert result.success is True
    assert (
        result.data["investigation"]["status"]
        == "created"
    )


def test_get_investigation_status_returns_compact_state():
    result = run_tool(
        "get_investigation_status",
        {
            "investigation_id": "inv-1",
        },
    )

    assert result.success is True
    assert result.data["status"] == "created"
    assert result.data["selected_specialists"] == [
        "linux-cpu"
    ]


def test_get_evidence_reads_runtime_evidence():
    result = run_tool(
        "get_evidence",
        {
            "investigation_id": "inv-1",
        },
    )

    assert result.success is True
    assert result.data["evidence"] == [
        {
            "evidence_id": "ev-1",
            "kind": "command_result",
        }
    ]


def test_missing_investigation_is_controlled_error():
    result = run_tool(
        "get_investigation",
        {
            "investigation_id": "missing",
        },
    )

    assert result.success is False
    assert (
        result.error_code
        == "investigation_not_found"
    )
