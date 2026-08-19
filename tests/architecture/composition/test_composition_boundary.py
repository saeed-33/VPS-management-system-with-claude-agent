"""Tests for test composition boundary.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_composition_owns_the_application_container():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_composition_owns_the_application_container؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    composition = ROOT / "app/composition/__init__.py"
    text = composition.read_text(encoding="utf-8")

    assert "container = build_container()" in text
    assert '"container"' in text
    assert not (ROOT / "app/bootstrap.py").exists()


def test_composition_builder_owns_dependency_wiring():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_composition_builder_owns_dependency_wiring؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    builder = ROOT / "app/composition/builder.py"
    builder_text = builder.read_text(encoding="utf-8")

    container = ROOT / "app/composition/container.py"
    container_text = container.read_text(encoding="utf-8")

    assert (
        "from app.composition.container import ApplicationContainer"
        in builder_text
    )
    assert "class ApplicationContainer" not in builder_text
    assert "class ApplicationContainer" in container_text

    assert "def build_container()" in builder_text
    assert "return ApplicationContainer(" in builder_text

    assert "\ncontainer = build_container()" not in builder_text



def test_composition_package_exists_as_explicit_boundary():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_composition_package_exists_as_explicit_boundary؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    init_file = ROOT / "app/composition/__init__.py"
    text = init_file.read_text(encoding="utf-8")

    assert "ApplicationContainer" in text
    assert "build_container" in text
