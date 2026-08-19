"""Tests for test database model migration boundary.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]


def test_database_models_live_only_in_infrastructure():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_database_models_live_only_in_infrastructure؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    old_root = ROOT / "app/shared/database/models"
    new_root = ROOT / "app/infrastructure/database/models"

    new_files = {
        p.name for p in new_root.glob("*.py")
        if p.name != "__init__.py"
    }

    assert new_files
    assert not old_root.exists()

    for name in sorted(new_files):
        tree = ast.parse(
            (new_root / name).read_text(encoding="utf-8")
        )
        assert any(
            isinstance(node, ast.ClassDef)
            for node in tree.body
        )


def test_production_uses_infrastructure_model_imports():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_production_uses_infrastructure_model_imports؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    violations = []

    for path in (ROOT / "app").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "app.shared.database.models" in text:
            violations.append(str(path.relative_to(ROOT)))

    assert violations == []


def test_engine_registers_infrastructure_models():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_engine_registers_infrastructure_models؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    text = (
        ROOT / "app/infrastructure/database/engine.py"
    ).read_text(encoding="utf-8")

    assert "import app.infrastructure.database.models" in text
    assert "import app.shared.database.models" not in text


def test_migrations_have_one_canonical_owner():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_migrations_have_one_canonical_owner؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    old_root = ROOT / "app/shared/database/migrations"
    new_root = ROOT / "app/infrastructure/database/migrations"

    new_files = {
        p.relative_to(new_root)
        for p in new_root.rglob("*")
        if p.is_file()
    }

    assert new_files
    assert not old_root.exists()
