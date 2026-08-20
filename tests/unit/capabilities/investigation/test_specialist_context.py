"""Tests for test specialist context.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.contracts.analysis.retrieved_analysis_context، app.core.contracts.investigation، app.core.contracts.knowledge_sources.knowledge_retrieval_context، app.capabilities.investigation.specialist_context، app.capabilities.investigation.specialist_registry.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio
from types import MappingProxyType

from app.core.contracts.analysis.retrieved_analysis_context import (
    RetrievedAnalysisContext,
)
from app.core.contracts.investigation.evidence_kind import EvidenceKind
from app.core.contracts.investigation.evidence_reference import EvidenceReference
from app.core.contracts.investigation.specialist_task import SpecialistTask
from app.core.contracts.knowledge_sources.knowledge_retrieval_context import KnowledgeRetrievalContext
from app.capabilities.investigation.specialist_context.specialist_context_budget import SpecialistContextBudget
from app.capabilities.investigation.specialist_context.specialist_context_builder import SpecialistContextBuilder
from app.capabilities.investigation.specialist_registry.specialist_runtime_definition import SpecialistRuntimeDefinition


def specialist():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى specialist؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SpecialistRuntimeDefinition(
        id=1,
        slug="nginx",
        name="NGINX Specialist",
        description=None,
        instructions=(
            "Diagnose NGINX only. "
            "Cite supplied evidence and knowledge."
        ),
        domains=(
            "nginx",
            "http",
            "proxy",
        ),
        trigger_hints=(),
        knowledge_topics=(
            "reverse proxy",
            "upstream",
        ),
        allowed_tool_ids=(),
        priority=10,
        max_rounds=2,
        max_actions=4,
        metadata=MappingProxyType({}),
    )


def task(
    *,
    evidence_ids=(),
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى task؛ المدخلات المهمة: evidence_ids.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SpecialistTask(
        task_id="task-1",
        investigation_id="inv-1",
        server_id=1,
        report_id=10,
        specialist_id="nginx",
        objective=(
            "Determine why proxy requests fail."
        ),
        evidence_ids=evidence_ids,
    )


def knowledge(
    chunk_id,
    *,
    content,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى knowledge؛ المدخلات المهمة: chunk_id، content.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return KnowledgeRetrievalContext(
        chunk_id=chunk_id,
        document_id=1,
        source_id=7,
        source_slug="nginx-docs",
        source_name="NGINX Docs",
        source_uri="https://nginx.org/en/docs/",
        document_title="NGINX documentation",
        canonical_uri="https://nginx.org/en/docs/",
        section_title="Proxy",
        page_number=None,
        content=content,
        rank=chunk_id,
        retrieval_strategy="hybrid",
        fusion_score=0.03,
        vector_score=0.8,
        full_text_score=0.1,
        vector_rank=1,
        full_text_rank=1,
        matched_specialist=True,
        matched_domains=("nginx",),
        source_priority=10,
    )


class Retriever:
    """
    يمثل Retriever جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, items):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: items.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.items = items
        self.call = None

    async def retrieve(self, **kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى retrieve؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.call = kwargs
        return list(self.items)


def test_context_preserves_knowledge_source_ids():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_context_preserves_knowledge_source_ids؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    retriever = Retriever(
        (
            knowledge(
                12,
                content=(
                    "proxy_pass forwards "
                    "requests upstream."
                ),
            ),
        )
    )

    builder = SpecialistContextBuilder(
        knowledge_retriever=retriever
    )

    snapshot = asyncio.run(
        builder.build(
            task=task(),
            specialist=specialist(),
            detected_domains=(
                "nginx",
                "proxy",
            ),
        )
    )

    assert (
        snapshot.knowledge_sources[0]
        .source_id
        == "knowledge-chunk:12"
    )

    assert (
        snapshot.knowledge_sources[0]
        .metadata["chunk_id"]
        == 12
    )

    assert (
        "knowledge_source_id: "
        "knowledge-chunk:12"
        in snapshot.rendered_context
    )


def test_irrelevant_evidence_is_excluded():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_irrelevant_evidence_is_excluded؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    retriever = Retriever(())

    evidence = (
        EvidenceReference(
            evidence_id="cpu-1",
            kind=(
                EvidenceKind
                .MONITORING_REPORT
            ),
            title="CPU",
            excerpt="CPU normal.",
        ),
        EvidenceReference(
            evidence_id="nginx-1",
            kind=(
                EvidenceKind
                .COMMAND_RESULT
            ),
            title="NGINX status",
            excerpt="502 response.",
        ),
    )

    builder = SpecialistContextBuilder(
        knowledge_retriever=retriever
    )

    snapshot = asyncio.run(
        builder.build(
            task=task(
                evidence_ids=(
                    "nginx-1",
                )
            ),
            specialist=specialist(),
            evidence=evidence,
        )
    )

    assert [
        item.evidence_id
        for item in snapshot.evidence
    ] == ["nginx-1"]

    assert "CPU normal." not in (
        snapshot.rendered_context
    )


def test_knowledge_budget_limits_large_results():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_knowledge_budget_limits_large_results؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    retriever = Retriever(
        tuple(
            knowledge(
                index,
                content=(
                    f"Chunk {index} "
                    + ("x" * 1_000)
                ),
            )
            for index in range(
                1,
                10,
            )
        )
    )

    builder = SpecialistContextBuilder(
        knowledge_retriever=retriever,
        budget=(
            SpecialistContextBudget(
                max_knowledge_chunks=3,
                max_knowledge_chars=2_300,
                max_total_chars=10_000,
            )
        ),
    )

    snapshot = asyncio.run(
        builder.build(
            task=task(),
            specialist=specialist(),
        )
    )

    assert (
        len(
            snapshot.knowledge_chunks
        )
        <= 3
    )

    assert (
        sum(
            len(item.content)
            for item
            in snapshot.knowledge_chunks
        )
        <= 2_300
    )


def test_context_includes_incident_provenance():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_context_includes_incident_provenance؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    retriever = Retriever(())

    incident = (
        RetrievedAnalysisContext(
            source_report_id=8,
            source_analysis_id=9,
            score=0.91,
            rank=1,
            health_status="warning",
            summary=(
                "Previous proxy timeout."
            ),
            issues=[
                {
                    "title": (
                        "Upstream timeout"
                    )
                }
            ],
            positive_findings=[],
            recommended_actions=[],
            retrieval_strategy="hybrid",
        )
    )

    builder = SpecialistContextBuilder(
        knowledge_retriever=retriever
    )

    snapshot = asyncio.run(
        builder.build(
            task=task(),
            specialist=specialist(),
            incident_contexts=(
                incident,
            ),
        )
    )

    assert (
        "[incident:report-8/analysis-9]"
        in snapshot.rendered_context
    )
