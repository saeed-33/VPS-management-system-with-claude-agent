import asyncio
import json

from app.interfaces.mcp.schemas import (
    ProjectToolDefinition,
    ProjectToolResult,
)
from app.interfaces.mcp.server import (
    ProjectMcpProtocolServer,
)


class ToolBoundary:
    def list_tools(
        self,
    ) -> list[ProjectToolDefinition]:
        return [
            ProjectToolDefinition(
                tool_id="get_server_context",
                description="Read server context.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "server_id": {
                            "type": "integer",
                        }
                    },
                },
            )
        ]

    async def execute(
        self,
        call,
    ) -> ProjectToolResult:
        if call.tool_id == "get_server_context":
            return ProjectToolResult(
                tool_id=call.tool_id,
                success=True,
                data={
                    "server": {
                        "id": call.arguments[
                            "server_id"
                        ]
                    }
                },
            )

        return ProjectToolResult(
            tool_id=call.tool_id,
            success=False,
            error_code="unknown_tool",
            error_message="Unknown tool.",
        )


def run_message(
    message,
):
    server = ProjectMcpProtocolServer(
        tool_boundary=ToolBoundary()
    )

    return asyncio.run(
        server.handle_message(message)
    )


def test_mcp_initialize_exposes_tool_capability():
    response = run_message(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
        }
    )

    assert response["result"]["capabilities"] == {
        "tools": {}
    }
    assert response["result"]["serverInfo"][
        "name"
    ] == "vps"


def test_mcp_tools_list_uses_project_tool_definitions():
    response = run_message(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
        }
    )

    tools = response["result"]["tools"]

    assert tools == [
        {
            "name": "get_server_context",
            "description": "Read server context.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "integer",
                    }
                },
            },
        }
    ]


def test_mcp_tools_call_returns_structured_project_result():
    response = run_message(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_server_context",
                "arguments": {
                    "server_id": 7,
                },
            },
        }
    )

    result = response["result"]
    content = json.loads(
        result["content"][0]["text"]
    )

    assert result["isError"] is False
    assert content["success"] is True
    assert content["data"] == {
        "server": {
            "id": 7,
        }
    }


def test_mcp_unknown_method_returns_jsonrpc_error():
    response = run_message(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "unknown/method",
        }
    )

    assert response["error"]["code"] == -32601
