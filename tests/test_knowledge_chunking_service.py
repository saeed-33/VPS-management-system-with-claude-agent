"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.knowledge.chunker، app.capabilities.knowledge.chunking_service.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from types import SimpleNamespace

from app.capabilities.knowledge.chunker import (
    KnowledgeChunkerConfig,
    StructureAwareKnowledgeChunker,
)
from app.capabilities.knowledge.chunking_service import (
    KnowledgeChunkingService,
)


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
        self.document = SimpleNamespace(
            id=7,
            source_id=3,
            status="parsed",
            document_metadata={
                "parsed_text": "CPU diagnostics. " * 100
            },
        )
        self.saved = None

    def get_by_id(self, document_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_by_id؛ المدخلات المهمة: document_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return self.document if document_id == 7 else None

    def replace_chunks(self, **kwargs):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى replace_chunks؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.saved = kwargs
        return SimpleNamespace(
            id=7,
            source_id=3,
            status="chunked",
            character_count=1700,
            chunks=[
                SimpleNamespace(**item)
                for item in kwargs["chunks"]
            ],
        )


def test_chunking_service_persists_chunks():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_chunking_service_persists_chunks؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repository = Repository()
    service = KnowledgeChunkingService(
        document_repository=repository,
        chunker=StructureAwareKnowledgeChunker(
            KnowledgeChunkerConfig(
                target_chars=300,
                max_chars=450,
                overlap_chars=40,
                min_chars=50,
            )
        ),
    )

    result = service.chunk_document(7)

    assert result.status == "chunked"
    assert repository.saved["document_id"] == 7
    assert repository.saved["chunks"]
    assert all(
        len(item["content_hash"]) == 64
        for item in repository.saved["chunks"]
    )
