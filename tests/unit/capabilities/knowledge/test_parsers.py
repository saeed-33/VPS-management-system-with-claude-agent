"""Tests for test parsers.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.knowledge.parsers.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from app.capabilities.knowledge.parsers.content_parser import KnowledgeContentParser
from app.capabilities.knowledge.parsers.text_normalization import normalize_text


def test_normalize_text_collapses_spacing():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_normalize_text_collapses_spacing؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert normalize_text(
        "  Alpha   beta\n\n\n Gamma "
    ) == "Alpha beta\n\nGamma"


def test_html_parser_removes_script_and_extracts_title():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_html_parser_removes_script_and_extracts_title؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    parser = KnowledgeContentParser()

    result = parser.parse(
        content=b"""
        <html>
          <head>
            <title>CPU Guide</title>
            <script>ignore_me()</script>
          </head>
          <body>
            <h1>CPU Scheduling</h1>
            <p>Check the run queue.</p>
          </body>
        </html>
        """,
        canonical_uri="https://example.com/cpu",
        media_type="text/html",
    )

    assert result.title == "CPU Guide"
    assert "CPU Scheduling" in result.text
    assert "Check the run queue." in result.text
    assert "ignore_me" not in result.text


def test_plain_text_parser():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_plain_text_parser؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    parser = KnowledgeContentParser()

    result = parser.parse(
        content=b"CPU usage is normal.",
        canonical_uri="inline://example",
        media_type="text/plain",
        title_hint="Example",
    )

    assert result.text == "CPU usage is normal."
    assert result.parser_name == "plain-text"
