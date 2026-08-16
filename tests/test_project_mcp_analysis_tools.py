"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.analysis.retrieval.rag_context، app.capabilities.knowledge.retrieval، app.interfaces.mcp.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio
from dataclasses import dataclass

from app.capabilities.analysis.retrieval.rag_context import (
    RetrievedAnalysisContext,
)
from app.capabilities.knowledge.retrieval import (
    KnowledgeRetrievalContext,
)
from app.interfaces.mcp import (
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
    """
    يمثل Analysis جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
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
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
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
    """
    يمثل AnalysisRepository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
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
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى find_completed_by_fingerprint؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        assert kwargs["server_id"] == 1
        assert kwargs["exclude_report_id"] == 10
        return self.exact

    def get_by_id(
        self,
        analysis_id,
    ):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_by_id؛ المدخلات المهمة: analysis_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.by_id.get(
            analysis_id
        )

    def get_by_report_id(
        self,
        report_id,
    ):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_by_report_id؛ المدخلات المهمة: report_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        if report_id == 10:
            return self.by_id[4]
        return None


class AnalysisOrchestrator:
    """
    يمثل AnalysisOrchestrator جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.calls = []

    async def process(
        self,
        *,
        report_id,
        server_id,
        force=False,
    ):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى process؛ المدخلات المهمة: report_id، server_id، force.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.calls.append(
            {
                "report_id": report_id,
                "server_id": server_id,
                "force": force,
            }
        )
        return 4


class IncidentRetriever:
    """
    يمثل IncidentRetriever جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    async def retrieve(
        self,
        **kwargs,
    ):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى retrieve؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
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
    """
    يمثل KnowledgeRetriever جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    async def retrieve(
        self,
        *,
        query,
        specialist_slug=None,
        domains=(),
    ):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى retrieve؛ المدخلات المهمة: query، specialist_slug، domains.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
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
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى boundary؛ المدخلات المهمة: analysis_repository، analysis_orchestrator، incident_retriever، knowledge_retriever.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
    """
    ينفذ مرحلة الأداة أو يحفظ نتيجة التقييم ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى run_tool؛ المدخلات المهمة: tool_id، arguments، tool_boundary.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_find_exact_report_match_returns_reusable_analysis؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_get_top_similar_reports_is_capped_at_three؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_analyze_report_uses_existing_orchestrator؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_get_analysis_by_report_id؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    result = run_tool(
        "get_analysis",
        {
            "report_id": 10,
        },
    )

    assert result.success is True
    assert result.data["analysis"]["id"] == 4


def test_search_knowledge_uses_project_retriever():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_search_knowledge_uses_project_retriever؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_missing_dependency_is_controlled_error؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
