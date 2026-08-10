from fastapi import FastAPI
from fastapi.testclient import TestClient

from admin_management_gap_closeout.payload.app.admin.api.diagnostic_tools import router


def test_diagnostic_tools_api_lists_registry():
    app = FastAPI()
    app.include_router(router)

    response = TestClient(app).get("/api/diagnostic-tools")

    assert response.status_code == 200
    by_id = {item["tool_id"]: item for item in response.json()}
    assert "systemd-status" in by_id
    assert "network-listeners" in by_id
    assert "nginx-config-test" in by_id
    assert by_id["systemd-status"]["risk"] == "read_only"
