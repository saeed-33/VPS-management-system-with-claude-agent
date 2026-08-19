"""Tests for test indexer.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.knowledge.indexer.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio
from types import SimpleNamespace

from app.capabilities.knowledge.indexer.indexer import KnowledgeIndexer


class EmbeddingClient:
    """
    يمثل EmbeddingClient جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    provider_name = "test"
    model_name = "test-model"
    dimensions = 3

    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.calls = []

    async def embed(self, text):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى embed؛ المدخلات المهمة: text.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.calls.append(text)
        return [0.1, 0.2, 0.3]


class Repository:
    """
    يمثل Repository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.updated = []
        self.marked = None
        self.document = SimpleNamespace(
            id=7,
            status="chunked",
            chunks=[
                SimpleNamespace(
                    id=10,
                    section_title="CPU Scheduling",
                    content="Inspect run queue.",
                    embedding=None,
                    embedding_provider=None,
                    embedding_model=None,
                    embedding_dimensions=None,
                ),
                SimpleNamespace(
                    id=11,
                    section_title=None,
                    content="Inspect load average.",
                    embedding=None,
                    embedding_provider=None,
                    embedding_model=None,
                    embedding_dimensions=None,
                ),
            ],
        )

    def get_by_id(self, document_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_by_id؛ المدخلات المهمة: document_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.document if document_id == 7 else None

    def update_chunk_embedding(self, **kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى update_chunk_embedding؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.updated.append(kwargs)

    def mark_indexed(self, document_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى mark_indexed؛ المدخلات المهمة: document_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.marked = document_id


def test_indexer_embeds_all_chunks_and_marks_document():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_indexer_embeds_all_chunks_and_marks_document؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repository = Repository()
    client = EmbeddingClient()
    indexer = KnowledgeIndexer(
        document_repository=repository,
        embedding_client=client,
    )

    result = asyncio.run(indexer.index_document(7))

    assert result.total_chunks == 2
    assert result.indexed_chunks == 2
    assert result.skipped_chunks == 0
    assert repository.marked == 7
    assert len(repository.updated) == 2
    assert client.calls[0].startswith(
        "CPU Scheduling\n\n"
    )


def test_indexer_skips_current_embedding():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_indexer_skips_current_embedding؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repository = Repository()
    chunk = repository.document.chunks[0]
    chunk.embedding = [0.1, 0.2, 0.3]
    chunk.embedding_provider = "test"
    chunk.embedding_model = "test-model"
    chunk.embedding_dimensions = 3

    client = EmbeddingClient()
    indexer = KnowledgeIndexer(
        document_repository=repository,
        embedding_client=client,
    )

    result = asyncio.run(indexer.index_document(7))

    assert result.indexed_chunks == 1
    assert result.skipped_chunks == 1


def test_force_reindexes_current_embedding():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_force_reindexes_current_embedding؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repository = Repository()

    for chunk in repository.document.chunks:
        chunk.embedding = [0.1, 0.2, 0.3]
        chunk.embedding_provider = "test"
        chunk.embedding_model = "test-model"
        chunk.embedding_dimensions = 3

    client = EmbeddingClient()
    indexer = KnowledgeIndexer(
        document_repository=repository,
        embedding_client=client,
    )

    result = asyncio.run(
        indexer.index_document(
            7,
            force=True,
        )
    )

    assert result.indexed_chunks == 2
    assert result.skipped_chunks == 0
