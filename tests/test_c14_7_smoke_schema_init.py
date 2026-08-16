"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SMOKE = ROOT / "tools" / "acceptance" / "smoke_ollama_claude_runtime.py"


def test_c14_7_smoke_initializes_schema_before_container():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_7_smoke_initializes_schema_before_container؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    text = SMOKE.read_text(encoding="utf-8")

    assert (
        "from app.infrastructure.database.engine import ("
        in text
    )
    assert "create_database_tables," in text
    assert "def prepare_database_schema()" in text

    schema_call = text.index(
        "    prepare_database_schema()"
    )
    container_call = text.index(
        "    container = build_container()"
    )

    assert schema_call < container_call


def test_c14_7_smoke_preserves_direct_project_import_fix():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_c14_7_smoke_preserves_direct_project_import_fix؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    text = SMOKE.read_text(encoding="utf-8")

    assert (
        "PROJECT_ROOT = Path(__file__).resolve().parents[2]"
        in text
    )
    assert "sys.path.insert(0, PROJECT_ROOT_TEXT)" in text
