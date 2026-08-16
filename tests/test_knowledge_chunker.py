"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.knowledge.chunker.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from app.capabilities.knowledge.chunker import (
    KnowledgeChunkerConfig,
    StructureAwareKnowledgeChunker,
)


def make_chunker():
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_chunker؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return StructureAwareKnowledgeChunker(
        KnowledgeChunkerConfig(
            target_chars=300,
            max_chars=450,
            overlap_chars=60,
            min_chars=50,
        )
    )


def test_markdown_heading_is_preserved_as_section():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_markdown_heading_is_preserved_as_section؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    chunks = make_chunker().chunk_document(
        text=(
            "# CPU Scheduling\n\n"
            + "Run queue diagnostics. " * 20
        )
    )

    assert chunks
    assert chunks[0].section_title == "CPU Scheduling"


def test_html_heading_metadata_is_used():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_html_heading_metadata_is_used؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    chunks = make_chunker().chunk_document(
        text=(
            "Overview\n\n"
            "General introduction.\n\n"
            "CPU Tuning\n\n"
            + "CPU details. " * 20
        ),
        metadata={
            "html_headings": ["Overview", "CPU Tuning"],
        },
    )

    assert any(
        chunk.section_title == "CPU Tuning"
        for chunk in chunks
    )


def test_pdf_page_metadata_preserves_page_number():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_pdf_page_metadata_preserves_page_number؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    chunks = make_chunker().chunk_document(
        text="fallback",
        metadata={
            "pages": [
                {
                    "page_number": 52,
                    "text": "CPU scheduling details. " * 12,
                },
            ],
        },
    )

    assert chunks
    assert all(chunk.page_number == 52 for chunk in chunks)


def test_large_document_is_split_under_max_chars():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_large_document_is_split_under_max_chars؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    text = "\n\n".join(
        f"Paragraph {index}. "
        + ("Diagnostic detail. " * 12)
        for index in range(20)
    )

    chunks = make_chunker().chunk_document(text=text)

    assert len(chunks) > 1
    assert all(len(chunk.content) <= 450 for chunk in chunks)


def test_chunk_indexes_are_contiguous():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_chunk_indexes_are_contiguous؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    chunks = make_chunker().chunk_document(
        text="\n\n".join(
            ("Diagnostic information. " * 12)
            for _ in range(8)
        )
    )

    assert [
        chunk.chunk_index
        for chunk in chunks
    ] == list(range(len(chunks)))
