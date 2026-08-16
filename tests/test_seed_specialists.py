"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.policies.diagnostic_tools.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from app.core.policies.diagnostic_tools import (
    build_default_diagnostic_tool_registry,
)
from tools.dev.seed_specialists import (
    SPECIALISTS,
    build_create_dto,
    build_update_dto,
)


def test_seeded_specialists_reference_registered_read_only_tools():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_seeded_specialists_reference_registered_read_only_tools؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    registered = {
        item.tool_id
        for item in build_default_diagnostic_tool_registry().definitions
    }

    for definition in SPECIALISTS:
        allowed = set(definition["allowed_tool_ids"])
        assert allowed
        assert allowed <= registered
        assert set(build_create_dto(definition).allowed_tool_ids) == allowed
        assert set(build_update_dto(definition).allowed_tool_ids) == allowed
