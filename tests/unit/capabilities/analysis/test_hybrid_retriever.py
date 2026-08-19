"""Tests for test hybrid retriever.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.analysis.retrieval.full_text_retriever، app.capabilities.analysis.retrieval.hybrid_retriever، app.capabilities.analysis.retrieval.rag_context، app.capabilities.analysis.retrieval.structured_compatibility.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio
import json
from dataclasses import dataclass

import pytest

from app.capabilities.analysis.retrieval.full_text_retriever.candidate import FullTextCandidate
from app.capabilities.analysis.retrieval.hybrid_retriever.retriever import HybridRetriever
from app.capabilities.analysis.retrieval.rag_context import (
    RetrievedAnalysisContext,
)
from app.capabilities.analysis.retrieval.structured_compatibility.checker import StructuredCompatibilityChecker


@dataclass
class FakeAnalysis:
    """
    يمثل FakeAnalysis جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    status: str = "completed"
    health_status: str = "healthy"
    summary: str = "summary"
    issues: list | None = None
    positive_findings: list | None = None
    recommended_actions: list | None = None

    def __post_init__(self):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __post_init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.issues = self.issues or []
        self.positive_findings = (
            self.positive_findings or []
        )
        self.recommended_actions = (
            self.recommended_actions or []
        )


@dataclass
class FakeDocument:
    """
    يمثل FakeDocument جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    normalized_text: str


class FakeAnalysisRepository:
    """
    يمثل FakeAnalysisRepository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, analyses):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: analyses.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.analyses = analyses

    def get_by_id(self, analysis_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_by_id؛ المدخلات المهمة: analysis_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.analyses.get(analysis_id)


class FakeRetrievalRepository:
    """
    يمثل FakeRetrievalRepository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, documents=None):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: documents.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.documents = documents or {}

    def get_by_analysis_id(self, analysis_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_by_analysis_id؛ المدخلات المهمة: analysis_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.documents.get(analysis_id)


class FakeVectorRetriever:
    """
    يمثل FakeVectorRetriever جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, contexts):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: contexts.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.contexts = contexts

    async def retrieve(self, **kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى retrieve؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return list(self.contexts)


class FakeFullTextRetriever:
    """
    يمثل FakeFullTextRetriever جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, candidates):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: candidates.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.candidates = candidates

    def retrieve(self, **kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى retrieve؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return list(self.candidates)


def normalized_report(
    *,
    connection_successful=True,
    success=True,
    exit_status=0,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى normalized_report؛ المدخلات المهمة: connection_successful، success، exit_status.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return json.dumps(
        {
            "connection_successful": connection_successful,
            "error_message": "",
            "executions": [
                {
                    "command_id": 10,
                    "success": success,
                    "exit_status": exit_status,
                    "error_message": "",
                    "stderr": "",
                }
            ],
        },
        sort_keys=True,
    )


def vector_context(
    *,
    analysis_id,
    report_id,
    score,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى vector_context؛ المدخلات المهمة: analysis_id، report_id، score.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return RetrievedAnalysisContext(
        source_report_id=report_id,
        source_analysis_id=analysis_id,
        score=score,
        rank=1,
        health_status="healthy",
        summary="historical",
        issues=[],
        positive_findings=[],
        recommended_actions=[],
    )


def run_retrieve(retriever, current):
    """
    ينفذ مرحلة الأداة أو يحفظ نتيجة التقييم ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى run_retrieve؛ المدخلات المهمة: retriever، current.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return asyncio.run(
        retriever.retrieve(
            normalized_report=current,
            server_id=1,
            monitoring_profile_id=2,
            command_set_hash="abc",
            exclude_report_id=999,
        )
    )


def test_weak_vector_candidate_is_rejected_even_with_full_text():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_weak_vector_candidate_is_rejected_even_with_full_text؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    vector = FakeVectorRetriever(
        [
            vector_context(
                analysis_id=1,
                report_id=101,
                score=0.40,
            )
        ]
    )
    text = FakeFullTextRetriever(
        [
            FullTextCandidate(
                report_id=101,
                analysis_id=1,
                rank=99.0,
                health_status="healthy",
            )
        ]
    )

    retriever = HybridRetriever(
        analysis_repository=FakeAnalysisRepository(
            {1: FakeAnalysis()}
        ),
        retrieval_repository=FakeRetrievalRepository(),
        compatibility_checker=None,
        vector_retriever=vector,
        full_text_retriever=text,
        top_k=3,
        minimum_vector_score=0.72,
    )

    assert run_retrieve(
        retriever,
        normalized_report(),
    ) == []


def test_full_text_only_candidate_never_bypasses_vector_threshold():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_full_text_only_candidate_never_bypasses_vector_threshold؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    retriever = HybridRetriever(
        analysis_repository=FakeAnalysisRepository(
            {1: FakeAnalysis()}
        ),
        retrieval_repository=FakeRetrievalRepository(),
        compatibility_checker=None,
        vector_retriever=FakeVectorRetriever([]),
        full_text_retriever=FakeFullTextRetriever(
            [
                FullTextCandidate(
                    report_id=101,
                    analysis_id=1,
                    rank=500.0,
                    health_status="healthy",
                )
            ]
        ),
        minimum_vector_score=0.72,
    )

    assert run_retrieve(
        retriever,
        normalized_report(),
    ) == []


def test_hybrid_candidate_preserves_real_vector_similarity():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_hybrid_candidate_preserves_real_vector_similarity؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    vector = FakeVectorRetriever(
        [
            vector_context(
                analysis_id=1,
                report_id=101,
                score=0.96,
            )
        ]
    )
    text = FakeFullTextRetriever(
        [
            FullTextCandidate(
                report_id=101,
                analysis_id=1,
                rank=0.15,
                health_status="healthy",
            )
        ]
    )

    retriever = HybridRetriever(
        analysis_repository=FakeAnalysisRepository(
            {1: FakeAnalysis()}
        ),
        retrieval_repository=FakeRetrievalRepository(),
        compatibility_checker=None,
        vector_retriever=vector,
        full_text_retriever=text,
        top_k=1,
        rrf_k=60,
        minimum_vector_score=0.72,
    )

    contexts = run_retrieve(
        retriever,
        normalized_report(),
    )

    assert len(contexts) == 1
    context = contexts[0]
    assert context.retrieval_strategy == "hybrid"
    assert context.vector_score == pytest.approx(0.96)
    assert context.text_score == pytest.approx(0.15)
    assert context.score == pytest.approx(2 / 61)
    assert context.score != context.vector_score


def test_structural_conflict_rejects_high_similarity_candidate():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_structural_conflict_rejects_high_similarity_candidate؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    current = normalized_report(
        connection_successful=True,
    )
    historical = normalized_report(
        connection_successful=False,
    )

    retriever = HybridRetriever(
        analysis_repository=FakeAnalysisRepository(
            {1: FakeAnalysis()}
        ),
        retrieval_repository=FakeRetrievalRepository(
            {
                1: FakeDocument(
                    normalized_text=historical
                )
            }
        ),
        compatibility_checker=(
            StructuredCompatibilityChecker()
        ),
        vector_retriever=FakeVectorRetriever(
            [
                vector_context(
                    analysis_id=1,
                    report_id=101,
                    score=0.99,
                )
            ]
        ),
        full_text_retriever=None,
        minimum_vector_score=0.72,
    )

    assert run_retrieve(retriever, current) == []


def test_compatible_candidate_is_accepted():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_compatible_candidate_is_accepted؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    current = normalized_report()

    retriever = HybridRetriever(
        analysis_repository=FakeAnalysisRepository(
            {1: FakeAnalysis()}
        ),
        retrieval_repository=FakeRetrievalRepository(
            {
                1: FakeDocument(
                    normalized_text=current
                )
            }
        ),
        compatibility_checker=(
            StructuredCompatibilityChecker()
        ),
        vector_retriever=FakeVectorRetriever(
            [
                vector_context(
                    analysis_id=1,
                    report_id=101,
                    score=0.95,
                )
            ]
        ),
        full_text_retriever=None,
        minimum_vector_score=0.72,
    )

    contexts = run_retrieve(retriever, current)

    assert len(contexts) == 1
    assert contexts[0].vector_score == pytest.approx(0.95)


def test_duplicate_vector_and_text_candidate_becomes_one_context():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_duplicate_vector_and_text_candidate_becomes_one_context؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    vector = FakeVectorRetriever(
        [
            vector_context(
                analysis_id=1,
                report_id=101,
                score=0.93,
            )
        ]
    )
    text = FakeFullTextRetriever(
        [
            FullTextCandidate(
                report_id=101,
                analysis_id=1,
                rank=0.2,
                health_status="healthy",
            )
        ]
    )

    retriever = HybridRetriever(
        analysis_repository=FakeAnalysisRepository(
            {1: FakeAnalysis()}
        ),
        retrieval_repository=FakeRetrievalRepository(),
        compatibility_checker=None,
        vector_retriever=vector,
        full_text_retriever=text,
        top_k=3,
        minimum_vector_score=0.72,
    )

    contexts = run_retrieve(
        retriever,
        normalized_report(),
    )

    assert len(contexts) == 1
    assert contexts[0].source_analysis_id == 1
