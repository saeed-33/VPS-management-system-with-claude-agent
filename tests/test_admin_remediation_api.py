from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.capabilities.remediation.service import RemediationService
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.admin_auth import (
    AdminAuthAuditEventModel,
    AdminSessionModel,
    AdminUserModel,
)
from app.infrastructure.database.models.remediation import (
    RemediationApprovalModel,
    RemediationAuditEventModel,
    RemediationExecutionModel,
    RemediationPlanModel,
    SandboxValidationModel,
)
from app.infrastructure.database.repositories.remediation_repository import RemediationRepository
from app.interfaces.admin.api.remediation import router as remediation_router
from app.interfaces.admin.auth import AdminAuthMiddleware, AdminAuthService
from app.interfaces.admin.dependencies import get_remediation_service
from app.interfaces.admin.web import auth_router


@pytest.fixture()
def remediation_api_app():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    tables = [
        AdminUserModel.__table__,
        AdminSessionModel.__table__,
        AdminAuthAuditEventModel.__table__,
        RemediationPlanModel.__table__,
        RemediationApprovalModel.__table__,
        RemediationExecutionModel.__table__,
        SandboxValidationModel.__table__,
        RemediationAuditEventModel.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    auth_service = AdminAuthService(
        session_factory=session_factory,
        session_secret="test-remediation-session-secret",
    )
    for username, role in (("viewer", "viewer"), ("operator", "operator"), ("admin", "admin")):
        auth_service.create_admin(
            username=username,
            password=f"{username.title()}Password123!",
            role=role,
        )

    with session_factory() as session:
        session.add(
            RemediationPlanModel(
                plan_id="plan-api-repro",
                investigation_id="investigation-api-repro",
                title="API serialization regression",
                problem_summary="The persisted plan must remain a finite read model.",
                proposed_actions=[{"action_type": "start_service", "target": "demo"}],
                diagnosis_claim_ids=["claim-api-repro"],
                evidence_ids=["evidence-api-repro"],
                risk_level="low",
                plan_version=1,
                plan_fingerprint="fingerprint-api-repro",
                rollback_plan="Use the registered rollback action.",
                status="proposed",
                plan_metadata={"issue_fingerprint": "issue-api-repro"},
            )
        )
        session.commit()

    service = RemediationService(repository=RemediationRepository(session_factory))
    app = FastAPI()
    app.state.admin_auth_service = auth_service
    app.add_middleware(AdminAuthMiddleware, auth_service=auth_service)
    app.include_router(auth_router)
    app.include_router(remediation_router)
    app.dependency_overrides[get_remediation_service] = lambda: service
    yield app, auth_service
    Base.metadata.drop_all(engine, tables=list(reversed(tables)))
    engine.dispose()


def _login(client: TestClient, service: AdminAuthService, username: str) -> None:
    response = client.post(
        "/login",
        data={
            "username": username,
            "password": f"{username.title()}Password123!",
            "next": "/",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303


@pytest.mark.parametrize("username", ("viewer", "operator", "admin"))
def test_remediation_list_is_finite_json_and_preserves_frontend_shape(
    remediation_api_app, username
):
    app, service = remediation_api_app
    client = TestClient(app)
    _login(client, service, username)

    response = client.get("/api/remediation?limit=500")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    plan = payload[0]
    assert plan["plan_id"] == "plan-api-repro"
    assert plan["status"] == "proposed"
    assert plan["risk_level"] == "low"
    assert plan["plan_metadata"] == {"issue_fingerprint": "issue-api-repro"}
    assert plan["proposed_actions"][0]["action_type"] == "start_service"
    assert "metadata" not in plan
    encoded = json.dumps(payload)
    assert "MetaData" not in encoded
    assert "RecursionError" not in encoded
    assert "password" not in encoded.casefold()


def test_remediation_detail_and_missing_record_are_safe_json(remediation_api_app):
    app, service = remediation_api_app
    client = TestClient(app)
    _login(client, service, "operator")

    detail = client.get("/api/remediation/plan-api-repro")
    assert detail.status_code == 200
    assert detail.json()["plan"]["plan_id"] == "plan-api-repro"
    assert detail.json()["approval"] is None
    assert detail.json()["execution"] is None
    assert detail.json()["sandbox_validation"] is None

    missing = client.get("/api/remediation/does-not-exist")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Remediation plan not found."}
