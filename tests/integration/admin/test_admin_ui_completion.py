"""Tests for test admin ui completion.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.infrastructure.database.base، app.infrastructure.database.models.admin_auth، app.interfaces.admin.auth، app.interfaces.admin.api.servers، app.interfaces.admin.api.autonomous_remediation، app.interfaces.admin.web.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import re
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.admin_auth.audit_event import AdminAuthAuditEventModel
from app.infrastructure.database.models.admin_auth.session import AdminSessionModel
from app.infrastructure.database.models.admin_auth.user import AdminUserModel
from app.interfaces.admin.auth.middleware import AdminAuthMiddleware
from app.interfaces.admin.auth.service import AdminAuthService
from app.interfaces.admin.api.servers import _safety_designation
from app.interfaces.admin.api.autonomous_remediation import _reservation_view
from app.interfaces.admin.web.auth_routes import router
from app.interfaces.admin.web.routes import router as web_router


@pytest.fixture()
def ui_app():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى ui_app؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    tables = [
        AdminUserModel.__table__,
        AdminSessionModel.__table__,
        AdminAuthAuditEventModel.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    service = AdminAuthService(
        session_factory=session_factory,
        session_secret="ui-test-secret",
        session_ttl_seconds=3600,
    )
    for username, password, role in (
        ("viewer", "ViewerPassword123!", "viewer"),
        ("operator", "OperatorPassword123!", "operator"),
        ("admin", "AdminPassword123!", "admin"),
    ):
        service.create_admin(username=username, password=password, role=role)

    app = FastAPI()
    app.state.admin_auth_service = service
    app.add_middleware(AdminAuthMiddleware, auth_service=service)
    app.include_router(auth_router)
    app.include_router(web_router)
    yield app, service
    Base.metadata.drop_all(engine, tables=list(reversed(tables)))
    engine.dispose()


def login(client: TestClient, username: str, password: str):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى login؛ المدخلات المهمة: client، username، password.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    response = client.post(
        "/login",
        data={"username": username, "password": password, "next": "/"},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_all_admin_ui_pages_render_for_authenticated_roles(ui_app):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_all_admin_ui_pages_render_for_authenticated_roles؛ المدخلات المهمة: ui_app.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    app, _service = ui_app
    paths = [
        "/servers",
        "/monitoring-profiles",
        "/investigations",
        "/reports",
        "/specialists",
        "/remediation",
        "/autonomous-policies",
        "/autonomous-candidates",
        "/autonomous-history",
        "/autonomous-decisions",
        "/autonomous-runtime",
        "/autonomous-reservations",
        "/autonomous-authorizations",
        "/audit",
        "/system",
    ]
    for role, password in (
        ("viewer", "ViewerPassword123!"),
        ("operator", "OperatorPassword123!"),
        ("admin", "AdminPassword123!"),
    ):
        client = TestClient(app)
        login(client, role, password)
        for path in paths:
            response = client.get(path)
            assert response.status_code == 200, (role, path, response.text[:200])
    redirected_client = TestClient(app)
    login(redirected_client, "viewer", "ViewerPassword123!")
    redirected = redirected_client.get("/runtime-policies", follow_redirects=False)
    assert redirected.status_code == 307
    assert redirected.headers["location"] == "/autonomous-runtime"


def test_unauthenticated_new_ui_page_redirects_to_login(ui_app):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_unauthenticated_new_ui_page_redirects_to_login؛ المدخلات المهمة: ui_app.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    app, _service = ui_app
    response = TestClient(app).get("/autonomous-decisions", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login?next=")


def test_navigation_and_ui_safety_boundaries_are_present(ui_app):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_navigation_and_ui_safety_boundaries_are_present؛ المدخلات المهمة: ui_app.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    app, _service = ui_app
    client = TestClient(app)
    login(client, "viewer", "ViewerPassword123!")
    response = client.get("/autonomous-policies")
    assert response.status_code == 200
    for path in (
        "/autonomous-policies", "/autonomous-candidates", "/autonomous-history",
        "/autonomous-decisions", "/autonomous-runtime", "/autonomous-reservations",
        "/autonomous-authorizations", "/audit",
    ):
        assert f'href="{path}"' in response.text
    assert "data-required-permission=\"autonomous.policy.create\"" in response.text
    assert "force_execute" not in response.text
    assert "skip_policy" not in response.text
    assert "skip_sandbox" not in response.text
    assert "raw SQL" not in response.text
    assert "manual autonomous authorization" not in response.text


def test_remediation_ui_has_no_issue_fingerprint_input_or_arbitrary_execution(ui_app):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_remediation_ui_has_no_issue_fingerprint_input_or_arbitrary_execution؛ المدخلات المهمة: ui_app.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    app, _service = ui_app
    client = TestClient(app)
    login(client, "operator", "OperatorPassword123!")
    html = client.get("/remediation").text
    assert not re.search(r"<input[^>]+issue_fingerprint", html, re.IGNORECASE)
    assert "arbitrary shell" not in html.lower()
    assert "force_execute" not in html
    assert "skip_approval" not in html
    assert 'start_service: "بدء الخدمة"' in html
    assert 'item.target || item.service || "خدمة غير محددة"' in html


def test_safe_target_comes_only_from_persisted_designation():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_safe_target_comes_only_from_persisted_designation؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert _safety_designation(SimpleNamespace(description="safe-remediation-test non-production")) == "safe_remediation_lab"
    assert _safety_designation(SimpleNamespace(description="Production target")) == "production"
    assert _safety_designation(SimpleNamespace(description="phase5-lab")) == "unclassified"


def test_reservation_view_does_not_expose_owner_token():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_reservation_view_does_not_expose_owner_token؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    item = SimpleNamespace(
        reservation_id="r1", idempotency_key="safe-key", status="reserved",
        policy_id="p1", plan_id="plan-1", plan_fingerprint="fp",
        server_id=4, action_type="start_service", target="nginx",
        authorization_id=None, execution_id=None, owner_token="secret-owner",
        created_at=None, expires_at=None, completed_at=None,
    )
    result = _reservation_view(item)
    assert "owner_token" not in result
    assert "secret-owner" not in str(result)
