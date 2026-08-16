"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.infrastructure.database.models.specialist_definition، app.infrastructure.database.repositories.specialist_definition_repository، app.core.contracts.specialists.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database.models.specialist_definition import SpecialistDefinitionModel
from app.infrastructure.database.repositories.specialist_definition_repository import SpecialistDefinitionRepository
from app.core.contracts.specialists import CreateSpecialistDefinitionDTO, UpdateSpecialistDefinitionDTO


@pytest.fixture()
def repository() -> SpecialistDefinitionRepository:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى repository؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد SpecialistDefinitionRepository أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SpecialistDefinitionModel.__table__.create(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    return SpecialistDefinitionRepository(factory)


def make_specialist(slug="cpu", name="CPU Specialist", enabled=True, priority=100):
    """
    يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى make_specialist؛ المدخلات المهمة: slug، name، enabled، priority.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return CreateSpecialistDefinitionDTO(
        slug=slug,
        name=name,
        enabled=enabled,
        domains=["cpu", "performance", "cpu", " "],
        trigger_hints=["high cpu"],
        knowledge_topics=["linux cpu"],
        priority=priority,
        max_rounds=2,
        max_actions=4,
    )


def test_create_and_reload(repository):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_create_and_reload؛ المدخلات المهمة: repository.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    created = repository.create(make_specialist())
    reloaded = repository.get_by_id(created.id)
    assert reloaded is not None
    assert reloaded.slug == "cpu"
    assert reloaded.domains == ["cpu", "performance"]


def test_slug_is_normalized(repository):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_slug_is_normalized؛ المدخلات المهمة: repository.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    created = repository.create(CreateSpecialistDefinitionDTO(slug="  CPU  ", name="CPU"))
    assert created.slug == "cpu"
    assert repository.get_by_slug(" CPU ") is not None


def test_duplicate_slug_is_rejected(repository):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_duplicate_slug_is_rejected؛ المدخلات المهمة: repository.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repository.create(make_specialist())
    with pytest.raises(ValueError, match="slug already exists"):
        repository.create(make_specialist(name="Another CPU"))


def test_invalid_slug_is_rejected():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_invalid_slug_is_rejected؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    with pytest.raises(ValueError):
        CreateSpecialistDefinitionDTO(slug="CPU Specialist", name="CPU")


def test_update_specialist(repository):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_update_specialist؛ المدخلات المهمة: repository.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    created = repository.create(make_specialist())
    updated = repository.update(
        created.id,
        UpdateSpecialistDefinitionDTO(
            name="Linux CPU Investigator",
            domains=["cpu", "process"],
            priority=20,
            max_rounds=3,
            max_actions=6,
            metadata={"owner": "operations"},
        ),
    )
    assert updated is not None
    assert updated.name == "Linux CPU Investigator"
    assert updated.domains == ["cpu", "process"]
    assert updated.specialist_metadata == {"owner": "operations"}


def test_enabled_filter(repository):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_enabled_filter؛ المدخلات المهمة: repository.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    cpu = repository.create(make_specialist("cpu", "CPU", True, 20))
    repository.create(make_specialist("memory", "Memory", False, 10))
    assert [x.slug for x in repository.list_enabled()] == ["cpu"]
    repository.set_enabled(cpu.id, False)
    assert repository.list_enabled() == []


def test_priority_order(repository):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_priority_order؛ المدخلات المهمة: repository.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    repository.create(make_specialist("cpu", "CPU", True, 50))
    repository.create(make_specialist("memory", "Memory", True, 10))
    assert [x.slug for x in repository.list_all()] == ["memory", "cpu"]


def test_delete(repository):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_delete؛ المدخلات المهمة: repository.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    created = repository.create(make_specialist())
    assert repository.delete(created.id) is True
    assert repository.get_by_id(created.id) is None
