"""Tests for test specialist registry.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.investigation.specialist_registry.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from types import SimpleNamespace

import pytest

from app.capabilities.investigation.specialist_registry.specialist_registry import SpecialistRegistry
from app.capabilities.investigation.specialist_registry.specialist_registry_validation_error import SpecialistRegistryValidationError


def specialist(
    specialist_id: int,
    slug: str,
    *,
    enabled: bool = True,
    priority: int = 100,
    domains: list[str] | None = None,
    name: str | None = None,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى specialist؛ المدخلات المهمة: specialist_id، slug، enabled، priority، domains، name.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SimpleNamespace(
        id=specialist_id,
        slug=slug,
        name=name or slug,
        description=None,
        instructions=None,
        enabled=enabled,
        domains=domains or [],
        trigger_hints=[],
        knowledge_topics=[],
        allowed_tool_ids=[],
        priority=priority,
        max_rounds=2,
        max_actions=4,
        specialist_metadata={},
    )


class FakeRepository:
    """
    يمثل FakeRepository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, items):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: items.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.items = items
        self.calls = 0

    def list_enabled(self):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_enabled؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.calls += 1
        return [item for item in self.items if item.enabled]


def test_disabled_specialists_are_excluded():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_disabled_specialists_are_excluded؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    registry = SpecialistRegistry(
        FakeRepository([
            specialist(1, "cpu", domains=["cpu"]),
            specialist(2, "memory", enabled=False, domains=["memory"]),
        ])
    )

    assert [item.slug for item in registry.get_enabled()] == ["cpu"]


def test_snapshot_is_stable_and_uses_one_repository_read():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_snapshot_is_stable_and_uses_one_repository_read؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    cpu = specialist(1, "cpu", domains=["cpu"])
    repository = FakeRepository([cpu])
    registry = SpecialistRegistry(repository)

    snapshot = registry.snapshot()
    assert repository.calls == 1
    assert snapshot.get_by_slug("cpu") is not None

    cpu.enabled = False
    assert snapshot.get_by_slug("cpu") is not None
    assert registry.snapshot().get_by_slug("cpu") is None
    assert repository.calls == 2


def test_registry_order_is_deterministic():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_registry_order_is_deterministic؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    registry = SpecialistRegistry(
        FakeRepository([
            specialist(3, "zeta", priority=50, domains=["cpu"], name="Zeta"),
            specialist(2, "alpha", priority=20, domains=["cpu"], name="Alpha"),
            specialist(1, "beta", priority=20, domains=["cpu"], name="Beta"),
        ])
    )

    assert [item.slug for item in registry.get_enabled()] == [
        "alpha",
        "beta",
        "zeta",
    ]


def test_domain_lookup_is_case_insensitive():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_domain_lookup_is_case_insensitive؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    registry = SpecialistRegistry(
        FakeRepository([
            specialist(1, "cpu", domains=[" CPU ", "Process"]),
        ])
    )

    assert [item.slug for item in registry.find_by_domain(" cpu ")] == ["cpu"]
    assert [item.slug for item in registry.find_by_domain("PROCESS")] == ["cpu"]


def test_multi_domain_lookup_prefers_more_matches():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_multi_domain_lookup_prefers_more_matches؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    registry = SpecialistRegistry(
        FakeRepository([
            specialist(1, "cpu", priority=20, domains=["cpu", "performance"]),
            specialist(2, "process", priority=10, domains=["cpu", "process", "performance"]),
            specialist(3, "memory", priority=1, domains=["memory"]),
        ])
    )

    matches = registry.find_by_domains(["cpu", "process"])

    assert [match.specialist.slug for match in matches] == ["process", "cpu"]
    assert matches[0].matched_domains == ("cpu", "process")
    assert matches[0].coverage == 1.0


def test_require_all_filters_partial_matches():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_require_all_filters_partial_matches؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    registry = SpecialistRegistry(
        FakeRepository([
            specialist(1, "cpu", domains=["cpu"]),
            specialist(2, "process", domains=["cpu", "process"]),
        ])
    )

    matches = registry.find_by_domains(
        ["cpu", "process"],
        require_all=True,
    )

    assert [match.specialist.slug for match in matches] == ["process"]


def test_invalid_definition_fails_snapshot():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_invalid_definition_fails_snapshot؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    invalid = specialist(1, "cpu", domains=["cpu"])
    invalid.max_rounds = 0

    registry = SpecialistRegistry(FakeRepository([invalid]))

    with pytest.raises(
        SpecialistRegistryValidationError,
        match="max_rounds",
    ):
        registry.snapshot()


def test_invalid_domains_payload_fails_snapshot():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_invalid_domains_payload_fails_snapshot؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    invalid = specialist(1, "cpu", domains=["cpu"])
    invalid.domains = "cpu"

    registry = SpecialistRegistry(FakeRepository([invalid]))

    with pytest.raises(
        SpecialistRegistryValidationError,
        match="domains must be a JSON list",
    ):
        registry.snapshot()


def test_duplicate_domains_are_normalized():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_duplicate_domains_are_normalized؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    registry = SpecialistRegistry(
        FakeRepository([
            specialist(
                1,
                "cpu",
                domains=["CPU", " cpu ", "Process"],
            ),
        ])
    )

    item = registry.get_by_slug("cpu")

    assert item is not None
    assert item.domains == ("cpu", "process")
