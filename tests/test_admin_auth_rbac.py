"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.core.utils.datetime، app.infrastructure.database.base، app.infrastructure.database.models.admin_auth، app.interfaces.admin.auth، app.interfaces.admin.web.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.utils.datetime import utc_now
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.admin_auth import (
    AdminAuthAuditEventModel,
    AdminSessionModel,
    AdminUserModel,
)
from app.interfaces.admin.auth import AdminAuthMiddleware, AdminAuthService
from app.interfaces.admin.web import auth_router, router as web_router


@pytest.fixture()
def auth_app():
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى auth_app؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            AdminUserModel.__table__,
            AdminSessionModel.__table__,
            AdminAuthAuditEventModel.__table__,
        ],
    )
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    service = AdminAuthService(
        session_factory=session_factory,
        session_secret="test-admin-session-secret",
        session_ttl_seconds=3600,
    )
    service.create_admin(
        username="viewer",
        password="ViewerPassword123!",
        role="viewer",
    )
    service.create_admin(
        username="operator",
        password="OperatorPassword123!",
        role="operator",
    )
    service.create_admin(
        username="admin",
        password="AdminPassword123!",
        role="admin",
    )

    app = FastAPI()
    app.state.admin_auth_service = service
    app.add_middleware(AdminAuthMiddleware, auth_service=service)
    app.include_router(auth_router)
    app.include_router(web_router)

    @app.get("/api/reports")
    def reports():
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى reports؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return {"ok": True}

    @app.post("/api/servers")
    def create_server():
        """
        يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى create_server؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return {"ok": True}

    @app.patch("/api/servers/{server_id}")
    async def update_server(server_id: int, request: Request):
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى update_server؛ المدخلات المهمة: server_id، request.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return {"ok": True, "server_id": server_id, "payload": await request.json()}

    @app.post("/api/remediation/plan/approval/approval/approve")
    def approve():
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى approve؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return {"ok": True}

    @app.post("/api/remediation/plan/execute")
    def execute():
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى execute؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return {"ok": True}

    @app.post("/api/remediation/plan/rollback")
    def rollback():
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى rollback؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return {"ok": True}

    @app.post("/api/autonomous-remediation/policies")
    def create_policy():
        """
        يبني أو يجهز البيانات اللازمة للمسار ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى create_policy؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
        return {"ok": True}

    yield app, service, session_factory
    Base.metadata.drop_all(
        engine,
        tables=[
            AdminAuthAuditEventModel.__table__,
            AdminSessionModel.__table__,
            AdminUserModel.__table__,
        ],
    )
    engine.dispose()


def login(client: TestClient, service: AdminAuthService, username: str, password: str):
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى login؛ المدخلات المهمة: client، service، username، password.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    response = client.post(
        "/login",
        data={"username": username, "password": password, "next": "/"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    raw_token = client.cookies.get(service.cookie_name)
    assert raw_token
    return service.csrf_token(raw_token)


def test_login_success_failure_logout_and_web_redirect(auth_app):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_login_success_failure_logout_and_web_redirect؛ المدخلات المهمة: auth_app.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    app, service, _session_factory = auth_app
    client = TestClient(app)

    protected = client.get("/servers", follow_redirects=False)
    assert protected.status_code == 303
    assert protected.headers["location"].startswith("/login?next=")

    failed = client.post(
        "/login",
        data={"username": "missing", "password": "wrong", "next": "/servers"},
        follow_redirects=False,
    )
    assert failed.status_code == 401
    assert "Invalid username or password" in failed.text

    csrf = login(client, service, "viewer", "ViewerPassword123!")
    assert client.get("/servers").status_code == 200

    logged_out = client.post(
        "/logout",
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert logged_out.status_code == 303
    assert client.get("/servers", follow_redirects=False).status_code == 303


@pytest.mark.parametrize(
    ("username", "password"),
    (
        ("viewer", "ViewerPassword123!"),
        ("operator", "OperatorPassword123!"),
        ("admin", "AdminPassword123!"),
    ),
)
def test_logout_form_csrf_revokes_session_and_clears_cookie(auth_app, username, password):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_logout_form_csrf_revokes_session_and_clears_cookie؛ المدخلات المهمة: auth_app، username، password.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    app, service, session_factory = auth_app
    client = TestClient(app)
    csrf = login(client, service, username, password)
    raw_token = client.cookies.get(service.cookie_name)
    assert raw_token

    missing = client.post("/logout", data={}, follow_redirects=False)
    assert missing.status_code == 403
    assert client.get("/servers").status_code == 200

    invalid = client.post(
        "/logout", data={"csrf_token": "invalid"}, follow_redirects=False
    )
    assert invalid.status_code == 403
    assert client.get("/servers").status_code == 200

    logged_out = client.post(
        "/logout", data={"csrf_token": csrf}, follow_redirects=False
    )
    assert logged_out.status_code == 303
    assert logged_out.headers["location"] == "/login"
    assert "Max-Age=0" in logged_out.headers["set-cookie"]
    assert f"{service.cookie_name}={raw_token}" not in logged_out.headers["set-cookie"]
    assert raw_token not in logged_out.text

    with session_factory() as session:
        model = session.scalar(
            select(AdminSessionModel).where(
                AdminSessionModel.session_digest == service._digest(raw_token)
            )
        )
        assert model is not None
        assert model.revoked_at is not None
    assert client.get("/servers", follow_redirects=False).status_code == 303


def test_unauthenticated_logout_is_safe(auth_app):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_unauthenticated_logout_is_safe؛ المدخلات المهمة: auth_app.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    app, _service, _session_factory = auth_app
    response = TestClient(app).post("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login?next=%2Flogout"


def test_api_authentication_and_csrf_fail_closed(auth_app):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_api_authentication_and_csrf_fail_closed؛ المدخلات المهمة: auth_app.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    app, service, _session_factory = auth_app
    client = TestClient(app)

    assert client.get("/api/reports").status_code == 401
    csrf = login(client, service, "admin", "AdminPassword123!")

    assert client.post("/api/servers", json={}).status_code == 403
    assert client.post(
        "/api/servers", json={}, headers={"X-CSRF-Token": "invalid"}
    ).status_code == 403
    assert client.post(
        "/api/servers", json={}, headers={"X-CSRF-Token": csrf}
    ).status_code == 200


def test_role_matrix_for_read_remediation_and_admin_operations(auth_app):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_role_matrix_for_read_remediation_and_admin_operations؛ المدخلات المهمة: auth_app.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    app, service, _session_factory = auth_app

    viewer = TestClient(app)
    viewer_csrf = login(viewer, service, "viewer", "ViewerPassword123!")
    assert viewer.get("/api/reports").status_code == 200
    assert viewer.post(
        "/api/servers", headers={"X-CSRF-Token": viewer_csrf}
    ).status_code == 403
    assert viewer.post(
        "/api/autonomous-remediation/policies",
        headers={"X-CSRF-Token": viewer_csrf},
    ).status_code == 403

    operator = TestClient(app)
    operator_csrf = login(operator, service, "operator", "OperatorPassword123!")
    for path in (
        "/api/remediation/plan/approval/approval/approve",
        "/api/remediation/plan/execute",
        "/api/remediation/plan/rollback",
    ):
        assert operator.post(path, headers={"X-CSRF-Token": operator_csrf}).status_code == 200
    assert operator.patch(
        "/api/servers/1",
        json={"monitor_enabled": True},
        headers={"X-CSRF-Token": operator_csrf},
    ).status_code == 200
    assert operator.patch(
        "/api/servers/1",
        json={"host": "changed.example"},
        headers={"X-CSRF-Token": operator_csrf},
    ).status_code == 403
    assert operator.post(
        "/api/autonomous-remediation/policies",
        headers={"X-CSRF-Token": operator_csrf},
    ).status_code == 403

    admin = TestClient(app)
    admin_csrf = login(admin, service, "admin", "AdminPassword123!")
    assert admin.post(
        "/api/servers", headers={"X-CSRF-Token": admin_csrf}
    ).status_code == 200
    assert admin.post(
        "/api/autonomous-remediation/policies",
        headers={"X-CSRF-Token": admin_csrf},
    ).status_code == 200
    for path in (
        "/api/remediation/plan/approval/approval/approve",
        "/api/remediation/plan/execute",
        "/api/remediation/plan/rollback",
    ):
        assert admin.post(path, headers={"X-CSRF-Token": admin_csrf}).status_code == 200


def test_expired_session_is_rejected_and_auth_events_are_audited(auth_app):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_expired_session_is_rejected_and_auth_events_are_audited؛ المدخلات المهمة: auth_app.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    app, service, session_factory = auth_app
    client = TestClient(app)
    login(client, service, "admin", "AdminPassword123!")
    raw_token = client.cookies.get(service.cookie_name)

    with session_factory() as session:
        model = session.scalar(
            select(AdminSessionModel).where(
                AdminSessionModel.session_digest == service._digest(raw_token)
            )
        )
        model.expires_at = utc_now() - timedelta(seconds=1)
        session.commit()

    assert client.get("/servers", follow_redirects=False).status_code == 303
    client.cookies.set(service.cookie_name, "invalid-session-token")
    assert client.get("/api/reports").status_code == 401

    with session_factory() as session:
        events = list(session.scalars(select(AdminAuthAuditEventModel)).all())
        event_types = {event.event_type for event in events}
        assert {"admin_created", "login_success"} <= event_types
        assert "password" not in " ".join(
            str(event.metadata_json).lower() for event in events
        )


def test_bootstrap_rejects_weak_and_duplicate_credentials(auth_app):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_bootstrap_rejects_weak_and_duplicate_credentials؛ المدخلات المهمة: auth_app.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    _app, service, _session_factory = auth_app
    with pytest.raises(ValueError, match="at least 12"):
        service.create_admin(username="weakuser", password="short", role="admin")
    with pytest.raises(ValueError, match="already exists"):
        service.create_admin(
            username="ADMIN",
            password="AnotherPassword123!",
            role="admin",
        )

    with _session_factory() as session:
        user = session.scalar(
            select(AdminUserModel).where(AdminUserModel.username == "admin")
        )
        assert user is not None
        assert user.password_hash.startswith("scrypt$")
        assert "AdminPassword123!" not in user.password_hash
