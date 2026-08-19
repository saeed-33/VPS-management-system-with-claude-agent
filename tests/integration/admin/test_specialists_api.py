"""Tests for test specialists api.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.interfaces.admin.api.specialists، app.interfaces.admin.dependencies، app.core.exceptions.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interfaces.admin.api.specialists import router
from app.interfaces.admin.dependencies import (
    get_specialist_definition_service,
)
from app.core.exceptions.duplicate_specialist_definition_error import DuplicateSpecialistDefinitionError
from app.core.exceptions.specialist_definition_not_found_error import SpecialistDefinitionNotFoundError


def model(
    specialist_id: int = 1,
    *,
    slug: str = "cpu",
    name: str = "CPU Specialist",
    enabled: bool = True,
):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى model؛ المدخلات المهمة: specialist_id، slug، name، enabled.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    now = datetime.now(UTC)

    return SimpleNamespace(
        id=specialist_id,
        slug=slug,
        name=name,
        description=None,
        instructions=None,
        enabled=enabled,
        domains=["cpu"],
        trigger_hints=[],
        knowledge_topics=["linux cpu"],
        allowed_tool_ids=[],
        priority=100,
        max_rounds=2,
        max_actions=4,
        specialist_metadata={},
        created_at=now,
        updated_at=now,
    )


class FakeService:
    """
    يمثل FakeService جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def __init__(self):
        """
        ينشئ الحالة الداخلية أو fixture المطلوبة ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.items = {
            1: model(),
        }

    def list_specialists(self, *, enabled_only=False):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_specialists؛ المدخلات المهمة: enabled_only.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        values = list(self.items.values())
        if enabled_only:
            values = [
                item
                for item in values
                if item.enabled
            ]
        return values

    def get_specialist(self, specialist_id):
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى get_specialist؛ المدخلات المهمة: specialist_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        item = self.items.get(specialist_id)
        if item is None:
            raise SpecialistDefinitionNotFoundError(
                specialist_id
            )
        return item

    def create_specialist(self, data):
        """
        يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى create_specialist؛ المدخلات المهمة: data.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        if data.slug == "duplicate":
            raise DuplicateSpecialistDefinitionError(
                data.slug
            )
        item = model(
            2,
            slug=data.slug.strip().lower(),
            name=data.name,
            enabled=data.enabled,
        )
        self.items[item.id] = item
        return item

    def update_specialist(self, specialist_id, data):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى update_specialist؛ المدخلات المهمة: specialist_id، data.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        item = self.get_specialist(specialist_id)
        if data.name is not None:
            item.name = data.name
        return item

    def set_enabled(self, specialist_id, enabled):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى set_enabled؛ المدخلات المهمة: specialist_id، enabled.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        item = self.get_specialist(specialist_id)
        item.enabled = enabled
        return item

    def delete_specialist(self, specialist_id):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى delete_specialist؛ المدخلات المهمة: specialist_id.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        self.get_specialist(specialist_id)
        del self.items[specialist_id]


def client():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى client؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    app = FastAPI()
    service = FakeService()

    app.dependency_overrides[
        get_specialist_definition_service
    ] = lambda: service

    app.include_router(router)

    return TestClient(app), service


def test_list_specialists():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_list_specialists؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    api, _ = client()

    response = api.get(
        "/api/specialists"
    )

    assert response.status_code == 200
    assert response.json()[0]["slug"] == "cpu"


def test_create_specialist():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_create_specialist؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    api, _ = client()

    response = api.post(
        "/api/specialists",
        json={
            "slug": "memory",
            "name": "Memory Specialist",
        },
    )

    assert response.status_code == 201
    assert response.json()["slug"] == "memory"


def test_duplicate_specialist_returns_409():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_duplicate_specialist_returns_409؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    api, _ = client()

    response = api.post(
        "/api/specialists",
        json={
            "slug": "duplicate",
            "name": "Duplicate",
        },
    )

    assert response.status_code == 409


def test_update_and_enable():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_update_and_enable؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    api, _ = client()

    response = api.patch(
        "/api/specialists/1",
        json={
            "name": "Linux CPU Investigator",
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["name"]
        == "Linux CPU Investigator"
    )

    response = api.put(
        "/api/specialists/1/enabled",
        json={
            "enabled": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["enabled"] is False


def test_missing_specialist_returns_404():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_missing_specialist_returns_404؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    api, _ = client()

    response = api.get(
        "/api/specialists/999"
    )

    assert response.status_code == 404


def test_delete_specialist():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_delete_specialist؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    api, _ = client()

    response = api.delete(
        "/api/specialists/1"
    )

    assert response.status_code == 204
