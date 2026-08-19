"""Tests for test hybrid retrieval.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.knowledge.retrieval، app.infrastructure.database.repositories.knowledge_retrieval_repository.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio

from app.capabilities.knowledge.retrieval.retriever import KnowledgeHybridRetriever
from app.infrastructure.database.repositories.knowledge_retrieval_repository.search_row import KnowledgeSearchRow


class EmbeddingClient:
    """
    يمثل EmbeddingClient جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    provider_name = "test"
    model_name = "test-model"
    dimensions = 3

    async def embed(self, text):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى embed؛ المدخلات المهمة: text.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return [0.1, 0.2, 0.3]


def row(
    chunk_id,
    *,
    score,
    specialist_slugs=(),
    domains=(),
    priority=10,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى row؛ المدخلات المهمة: chunk_id، score، specialist_slugs، domains، priority.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return KnowledgeSearchRow(
        chunk_id=chunk_id,
        document_id=1,
        source_id=7,
        source_slug=f"source-{chunk_id}",
        source_name="Source",
        source_uri="https://example.com",
        source_priority=priority,
        domains=tuple(domains),
        specialist_slugs=tuple(specialist_slugs),
        document_title="Document",
        canonical_uri="https://example.com/doc",
        section_title="Section",
        page_number=None,
        content=f"Content {chunk_id}",
        score=score,
    )


class Repository:
    """
    يمثل Repository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def find_by_vector(self, **kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى find_by_vector؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return [
            row(
                1,
                score=0.90,
                specialist_slugs=("nginx",),
                domains=("http",),
            ),
            row(
                2,
                score=0.82,
                domains=("http",),
            ),
        ]

    def find_by_full_text(self, **kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى find_by_full_text؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return [
            row(
                2,
                score=0.50,
                domains=("http",),
            ),
            row(
                1,
                score=0.40,
                specialist_slugs=("nginx",),
                domains=("http",),
            ),
        ]


def test_hybrid_retrieval_fuses_both_branches():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_hybrid_retrieval_fuses_both_branches؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    retriever = KnowledgeHybridRetriever(
        repository=Repository(),
        embedding_client=EmbeddingClient(),
        top_k=2,
    )

    contexts = asyncio.run(
        retriever.retrieve(
            query="reverse proxy",
            specialist_slug="nginx",
            domains=("http",),
        )
    )

    assert len(contexts) == 2
    assert {
        item.retrieval_strategy
        for item in contexts
    } == {"hybrid"}


def test_specialist_scope_boosts_direct_source():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_specialist_scope_boosts_direct_source؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    retriever = KnowledgeHybridRetriever(
        repository=Repository(),
        embedding_client=EmbeddingClient(),
        top_k=2,
    )

    contexts = asyncio.run(
        retriever.retrieve(
            query="reverse proxy",
            specialist_slug="nginx",
            domains=("http",),
        )
    )

    assert contexts[0].chunk_id == 1
    assert contexts[0].matched_specialist is True


class VectorOnlyRepository:
    """
    يمثل VectorOnlyRepository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def find_by_vector(self, **kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى find_by_vector؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return [
            row(
                5,
                score=0.88,
                domains=("network",),
            )
        ]

    def find_by_full_text(self, **kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى find_by_full_text؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return []


def test_vector_only_candidate_is_allowed():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_vector_only_candidate_is_allowed؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    retriever = KnowledgeHybridRetriever(
        repository=VectorOnlyRepository(),
        embedding_client=EmbeddingClient(),
    )

    contexts = asyncio.run(
        retriever.retrieve(
            query="socket backlog",
            domains=("network",),
        )
    )

    assert len(contexts) == 1
    assert contexts[0].retrieval_strategy == "vector"
