from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interfaces.admin.web.routes import router


def make_client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_investigations_page_is_available():
    response = make_client().get("/investigations")

    assert response.status_code == 200
    assert "التحقيقات" in response.text
    assert "/api/investigations" in response.text


def test_investigation_detail_page_is_available():
    response = make_client().get("/investigations/inv-123")

    assert response.status_code == 200
    assert "تفاصيل التحقيق" in response.text
    assert "inv-123" in response.text
    assert "/api/investigations/" in response.text
