"""Tests for test ingestion contracts.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.knowledge.ingestion_contracts.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import pytest
from app.capabilities.knowledge.ingestion_contracts.chunk_draft import KnowledgeChunkDraft
from app.core.contracts.knowledge_sources.document_status import KnowledgeDocumentStatus
from app.core.contracts.knowledge_sources.parsed_document import ParsedKnowledgeDocument

def test_document_status_lifecycle_is_explicit():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_document_status_lifecycle_is_explicit؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert [x.value for x in KnowledgeDocumentStatus] == [
        "pending", "fetched", "parsed", "chunked", "indexed", "failed"
    ]

def test_parsed_document_requires_text():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_parsed_document_requires_text؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    with pytest.raises(ValueError, match="text must not be empty"):
        ParsedKnowledgeDocument(
            canonical_uri="https://example.com/doc",
            title="Example", media_type="text/html", text="   "
        )

def test_parsed_document_accepts_large_document_metadata():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_parsed_document_accepts_large_document_metadata؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    item = ParsedKnowledgeDocument(
        canonical_uri="file:///manual.pdf",
        title="Large Manual", media_type="application/pdf",
        text="Useful content", page_count=100, parser_name="pdf-parser"
    )
    assert item.page_count == 100

def test_chunk_draft_preserves_page_and_section():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_chunk_draft_preserves_page_and_section؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    chunk = KnowledgeChunkDraft(
        chunk_index=7, section_title="CPU Scheduling",
        page_number=52, content="Scheduler diagnostic guidance.",
        token_count=12
    )
    assert chunk.page_number == 52
    assert chunk.section_title == "CPU Scheduling"

def test_chunk_index_is_zero_based():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_chunk_index_is_zero_based؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    KnowledgeChunkDraft(chunk_index=0, content="First chunk")
    with pytest.raises(ValueError, match="chunk_index must be >= 0"):
        KnowledgeChunkDraft(chunk_index=-1, content="Invalid")
