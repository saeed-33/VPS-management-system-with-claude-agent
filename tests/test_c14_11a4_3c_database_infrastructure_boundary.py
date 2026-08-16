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
import ast


ROOT = Path(__file__).resolve().parents[1]


def test_database_core_implementation_lives_in_infrastructure():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_database_core_implementation_lives_in_infrastructure؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    infra = ROOT / "app/infrastructure/database"
    for name in ("base.py", "engine.py", "session.py"):
        path = infra / name
        assert path.is_file()
        assert path.read_text(encoding="utf-8").strip()


def test_repository_implementations_live_only_in_infrastructure():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_repository_implementations_live_only_in_infrastructure؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    infra_root = ROOT / "app/infrastructure/database/repositories"
    shared_root = ROOT / "app/shared/database/repositories"

    infra_files = {
        p.name for p in infra_root.glob("*.py")
        if p.name != "__init__.py"
    }

    assert infra_files
    assert not shared_root.exists()

    for name in sorted(infra_files):
        tree = ast.parse(
            (infra_root / name).read_text(encoding="utf-8")
        )
        assert any(
            isinstance(node, (ast.ClassDef, ast.FunctionDef))
            for node in tree.body
        )


def test_production_composition_uses_infrastructure_repositories():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_production_composition_uses_infrastructure_repositories؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    text = (
        ROOT / "app/composition/repositories.py"
    ).read_text(encoding="utf-8")

    assert "app.infrastructure.database.repositories" in text
    assert "app.shared.database.repositories" not in text


def test_shared_database_package_is_removed_after_boundary_closure():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_shared_database_package_is_removed_after_boundary_closure؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert not (ROOT / "app/shared/database").exists()
