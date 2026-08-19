"""Tests for test source foundation.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.capabilities.knowledge.source_registry، app.core.contracts.knowledge_sources.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from types import SimpleNamespace

import pytest

from app.capabilities.knowledge.source_registry.registry import KnowledgeSourceRegistry
from app.core.contracts.knowledge_sources.create_knowledge_source_dto import CreateKnowledgeSourceDTO


class FakeRepository:
    """
    يمثل FakeRepository جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self, items=None):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: items.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.items = list(
            items or []
        )

    def list_enabled(self):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_enabled؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return [
            item
            for item in self.items
            if item.enabled
        ]


def source(
    source_id,
    slug,
    *,
    domains=(),
    specialist_slugs=(),
    enabled=True,
    priority=100,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى source؛ المدخلات المهمة: source_id، slug، domains، specialist_slugs، enabled، priority.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return SimpleNamespace(
        id=source_id,
        slug=slug,
        name=slug,
        description=None,
        source_type="url",
        source_uri=(
            "https://example.com/"
            + slug
        ),
        inline_content=None,
        enabled=enabled,
        domains=list(domains),
        specialist_slugs=list(
            specialist_slugs
        ),
        tags=[],
        priority=priority,
        source_metadata={},
    )


def test_url_source_requires_uri():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_url_source_requires_uri؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    with pytest.raises(
        ValueError,
        match="requires source_uri",
    ):
        CreateKnowledgeSourceDTO(
            slug="linux-docs",
            name="Linux docs",
            source_type="url",
        )


def test_inline_source_requires_content():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_inline_source_requires_content؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    with pytest.raises(
        ValueError,
        match="requires inline_content",
    ):
        CreateKnowledgeSourceDTO(
            slug="internal-runbook",
            name="Internal Runbook",
            source_type="inline",
        )


def test_create_dto_normalizes_scope():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_create_dto_normalizes_scope؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    dto = CreateKnowledgeSourceDTO(
        slug="Linux-CPU-Docs",
        name=" Linux CPU Docs ",
        source_type="URL",
        source_uri=" https://example.com/cpu ",
        domains=(
            " CPU ",
            "cpu",
            "Performance",
        ),
        specialist_slugs=(
            "linux-cpu",
            "LINUX-CPU",
        ),
    )

    assert dto.slug == "linux-cpu-docs"
    assert dto.name == "Linux CPU Docs"
    assert dto.source_type == "url"
    assert dto.domains == (
        "cpu",
        "performance",
    )
    assert dto.specialist_slugs == (
        "linux-cpu",
    )


def test_registry_excludes_disabled_sources():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_registry_excludes_disabled_sources؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    registry = KnowledgeSourceRegistry(
        FakeRepository(
            [
                source(
                    1,
                    "enabled",
                    enabled=True,
                ),
                source(
                    2,
                    "disabled",
                    enabled=False,
                ),
            ]
        )
    )

    assert [
        item.slug
        for item
        in registry.snapshot().sources
    ] == ["enabled"]


def test_registry_finds_sources_by_domain():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_registry_finds_sources_by_domain؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    registry = KnowledgeSourceRegistry(
        FakeRepository(
            [
                source(
                    1,
                    "cpu-guide",
                    domains=("cpu",),
                    priority=20,
                ),
                source(
                    2,
                    "network-guide",
                    domains=("network",),
                    priority=10,
                ),
            ]
        )
    )

    assert [
        item.slug
        for item in (
            registry.snapshot()
            .find_by_domain("CPU")
        )
    ] == ["cpu-guide"]


def test_registry_finds_sources_for_specialist():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_registry_finds_sources_for_specialist؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    registry = KnowledgeSourceRegistry(
        FakeRepository(
            [
                source(
                    1,
                    "cpu-guide",
                    specialist_slugs=(
                        "linux-cpu",
                    ),
                ),
                source(
                    2,
                    "generic-guide",
                ),
            ]
        )
    )

    assert [
        item.slug
        for item in (
            registry.snapshot()
            .find_for_specialist(
                "LINUX-CPU"
            )
        )
    ] == ["cpu-guide"]
