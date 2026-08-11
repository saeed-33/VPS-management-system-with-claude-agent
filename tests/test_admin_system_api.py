from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.admin.api.system import router
from app.admin.dependencies import (
    get_claude_supervisor,
    get_project_tool_boundary,
)
from app.mcp.schemas import ProjectToolDefinition


class FakeSupervisor:
    @property
    def status(self) -> dict:
        return {
            "runtime": "claude",
            "state": "active",
        }


class FakeToolBoundary:
    def list_tool_groups(
        self,
    ) -> dict[str, list[ProjectToolDefinition]]:
        return {
            "monitoring": [
                ProjectToolDefinition(
                    tool_id="run_monitoring",
                    description="Run monitoring.",
                    input_schema={
                        "type": "object",
                    },
                    read_only=False,
                )
            ],
            "reports": [
                ProjectToolDefinition(
                    tool_id="get_report",
                    description="Read report.",
                    input_schema={
                        "type": "object",
                    },
                    read_only=True,
                )
            ],
        }


def test_system_runtime_api_exposes_supervisor_and_tools():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[
        get_claude_supervisor
    ] = FakeSupervisor
    app.dependency_overrides[
        get_project_tool_boundary
    ] = FakeToolBoundary

    response = TestClient(app).get(
        "/api/system/runtime"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["supervisor"] == {
        "runtime": "claude",
        "state": "active",
    }
    assert payload["tool_count"] == 2
    assert [
        group["name"]
        for group in payload["tool_groups"]
    ] == [
        "monitoring",
        "reports",
    ]
    assert (
        payload["tool_groups"][0]["tools"][0][
            "read_only"
        ]
        is False
    )
