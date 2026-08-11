from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.admin.web.routes import router


def test_system_runtime_page_is_available():
    app = FastAPI()
    app.include_router(router)

    response = TestClient(app).get("/system")

    assert response.status_code == 200
    assert "System Runtime" in response.text
    assert "/api/system/runtime" in response.text
