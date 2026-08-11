import asyncio
from dataclasses import dataclass

from app.domain.analysis.retrieval.rag_context import (
    RetrievedAnalysisContext,
)
from app.domain.knowledge.retrieval import (
    KnowledgeRetrievalContext,
)
from app.mcp import (
    ProjectMcpToolBoundary,
    ProjectToolCall,
)

from tests.test_project_mcp_tool_boundary import (
    MonitoringService,
    ProfileService,
    ReportService,
    ServerService,
)


@dataclass
class Analysis:
    id: int
    report_id: int
    server_id: int = 1
    provider_name: str = "ollama"
    model_name: str = "qwen3:8b"
    status: str = "completed"
    health_status: str = "degraded"
    summary: str = "CPU pressure."
    issues: list = None
    positive_findings: list = None
    recommended_actions: list = None
    analysis_source: str = "generated"
    reused_from_analysis_id: int | None = None
    retrieval_strategy: str | None = None
    retrieval_score: float | None = None
    llm_called: bool = True

    def __post_init__(self):
        self.issues = self.issues or [
            {
                "title": "High CPU",
            }
        ]
        self.positive_findings = (
            self.positive_findings or []
        )
        self.recommended_actions = (
            self.recommended_actions or []
        )


class AnalysisRepository:
    def __init__(self):
        self.exact = Analysis(
            id=3,
            report_id=8,
            analysis_source="reused",
            llm_called=False,
        )
        self.by_id = {
            3: self.exact,
            4: Analysis(
                id=4,
                report_id=10,
            ),
        }

    def find_completed_by_fingerprint(
        self,
        **kwargs,
    ):
        assert kwargs["server_id"] == 1
        assert kwargs["exclude_report_id"] == 10
        return self.exact

    def get_by_id(
        self,
        analysis_id,
    ):
        return self.by_id.get(
            analysis_id
        )

    def get_by_report_id(
        self,
        report_id,
    ):
        if report_id == 10:
            return self.by_id[4]
        return None


class AnalysisOrchestrator:
    def __init__(self):
        self.calls = []

    async def process(
        self,
        *,
        report_id,
        server_id,
        force=False,
    ):
        self.calls.append(
            {
                "report_id": report_id,
                "server_id": server_id,
                "force": force,
            }
        )
        return 4


class IncidentRetriever:
    async def retrieve(
        self,
        **kwargs,
    ):
        assert kwargs["server_id"] == 1
        assert kwargs["exclude_report_id"] == 10
        return [
            RetrievedAnalysisContext(
                source_report_id=i,
                source_analysis_id=i + 100,
                score=0.9 - (i * 0.01),
                rank=i,
                health_status="degraded",
                summary=f"Similar {i}",
                issues=[],
                positive_findings=[],
                recommended_actions=[],
                retrieval_strategy="hybrid",
                vector_score=0.8,
            )
            for i in range(1, 5)
        ]


class KnowledgeRetriever:
    async def retrieve(
        self,
        *,
        query,
        specialist_slug=None,
        domains=(),
    ):
        assert query == "nginx cpu"
        assert specialist_slug == "web"
        assert domains == ("nginx",)
        return [
            KnowledgeRetrievalContext(
                chunk_id=1,
                document_id=2,
                source_id=3,
                source_slug="nginx-docs",
                source_name="Nginx Docs",
                source_uri="https://example.test",
                document_title="Nginx",
                canonical_uri="https://example.test/nginx",
                section_title="CPU",
                page_number=None,
                content="Tune worker processes.",
                rank=1,
                retrieval_strategy="hybrid",
                fusion_score=0.5,
                vector_score=0.8,
                full_text_score=0.2,
                vector_rank=1,
                full_text_rank=1,
                matched_specialist=True,
                matched_domains=("nginx",),
                source_priority=1,
            )
        ]


def boundary(
    *,
    analysis_repository=None,
    analysis_orchestrator=None,
    incident_retriever=None,
    knowledge_retriever=None,
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
        analysis_orchestrator=(
            analysis_orchestrator
            if analysis_orchestrator is not None
            else AnalysisOrchestrator()
        ),
        incident_retriever=(
            incident_retriever
            if incident_retriever is not None
            else IncidentRetriever()
        ),
        knowledge_retriever=(
            knowledge_retriever
            if knowledge_retriever is not None
            else KnowledgeRetriever()
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


def test_find_exact_report_match_returns_reusable_analysis():
    result = run_tool(
        "find_exact_report_match",
        {
            "report_id": 10,
        },
    )

    assert result.success is True
    assert result.data["matched"] is True
    assert result.data["analysis"]["id"] == 3
    assert (
        result.data["analysis"]["llm_called"]
        is False
    )
    assert result.data["report_fingerprint"]


def test_get_top_similar_reports_is_capped_at_three():
    result = run_tool(
        "get_top_similar_reports",
        {
            "report_id": 10,
            "limit": 99,
        },
    )

    assert result.success is True
    assert result.data["limit"] == 3
    assert len(result.data["similar_reports"]) == 3
    assert (
        result.data["similar_reports"][0][
            "source_report_id"
        ]
        == 1
    )


def test_analyze_report_uses_existing_orchestrator():
    orchestrator = AnalysisOrchestrator()
    result = run_tool(
        "analyze_report",
        {
            "report_id": 10,
            "force": True,
        },
        tool_boundary=boundary(
            analysis_orchestrator=orchestrator
        ),
    )

    assert result.success is True
    assert result.data["analysis_id"] == 4
    assert result.data["analysis"]["id"] == 4
    assert orchestrator.calls == [
        {
            "report_id": 10,
            "server_id": 1,
            "force": True,
        }
    ]


def test_get_analysis_by_report_id():
    result = run_tool(
        "get_analysis",
        {
            "report_id": 10,
        },
    )

    assert result.success is True
    assert result.data["analysis"]["id"] == 4


def test_search_knowledge_uses_project_retriever():
    result = run_tool(
        "search_knowledge",
        {
            "query": "nginx cpu",
            "specialist_slug": "web",
            "domains": ["nginx"],
            "limit": 6,
        },
    )

    assert result.success is True
    assert result.data["knowledge"][0]["chunk_id"] == 1
    assert (
        result.data["knowledge"][0][
            "matched_domains"
        ]
        == ["nginx"]
    )


def test_missing_dependency_is_controlled_error():
    tool_boundary = ProjectMcpToolBoundary(
        server_service=ServerService(),
        monitoring_profile_service=(
            ProfileService()
        ),
        monitoring_service=MonitoringService(),
        report_query_service=ReportService(),
    )

    result = run_tool(
        "analyze_report",
        {
            "report_id": 10,
        },
        tool_boundary=tool_boundary,
    )

    assert result.success is False
    assert result.error_code == "validation_error"
    assert "analysis_orchestrator" in (
        result.error_message
    )
