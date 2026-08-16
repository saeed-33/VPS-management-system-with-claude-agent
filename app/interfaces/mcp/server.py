"""
خادم MCP الخاص بالمشروع.

يتعامل مع رسائل initialize وtools/list وtools/call، ويحوّلها إلى نتائج JSON-RPC
مع رسائل خطأ منظمة، ويوفر تشغيلًا عبر stdin/stdout.
"""
from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import asdict
from typing import Any, TextIO

from app.interfaces.mcp.schemas import (
    ProjectToolCall,
    ProjectToolDefinition,
    ProjectToolResult,
)


class ProjectMcpProtocolServer:
    """
    ينفذ رسائل MCP الأساسية ويربطها بحد أدوات المشروع.
    """
    def __init__(
        self,
        *,
        tool_boundary,
        server_name: str = "vps",
        version: str = "0.1.0",
    ) -> None:
        """
        يربط حدود الأدوات ويجهز إصدار بروتوكول MCP وبيانات الخادم.
        """
        self._tool_boundary = tool_boundary
        self._server_name = server_name
        self._version = version

    async def handle_message(
        self,
        message: dict[str, Any],
    ) -> dict[str, Any] | None:
        """
        يفك رسالة JSON-RPC ويوجه initialize أو tools/list أو tools/call.
        """
        # يحول هذا الحد طلب Claude إلى قدرة من قدرات النظام، بينما يبقى قرار
        # الأثر والصلاحية داخل منطق المشروع.
        message_id = message.get("id")
        method = message.get("method")

        if method is None:
            return self._error_response(
                message_id,
                code=-32600,
                message="Missing JSON-RPC method.",
            )

        if method.startswith("notifications/"):
            return None

        try:
            if method == "initialize":
                result = self._initialize_result()
            elif method == "tools/list":
                result = self._tools_list_result()
            elif method == "tools/call":
                result = await self._tools_call_result(
                    message.get("params", {})
                )
            else:
                return self._error_response(
                    message_id,
                    code=-32601,
                    message=(
                        f"Unsupported MCP method: {method}"
                    ),
                )

        except Exception as exc:
            return self._error_response(
                message_id,
                code=-32603,
                message=str(exc),
            )

        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": result,
        }

    def _initialize_result(self) -> dict[str, Any]:
        """
        يبني استجابة تهيئة MCP ومعلومات القدرات.
        """
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": self._server_name,
                "version": self._version,
            },
        }

    def _tools_list_result(self) -> dict[str, Any]:
        """
        يبني استجابة قائمة الأدوات بصيغة MCP.
        """
        return {
            "tools": [
                self._serialize_tool_definition(
                    definition
                )
                for definition in (
                    self._tool_boundary.list_tools()
                )
            ]
        }

    async def _tools_call_result(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        ينفذ استدعاء أداة ويبني نتيجة MCP القابلة للعرض.
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not isinstance(tool_name, str):
            raise ValueError(
                "tools/call requires a string name."
            )

        if not isinstance(arguments, dict):
            raise ValueError(
                "tools/call arguments must be an object."
            )

        result = await self._tool_boundary.execute(
            ProjectToolCall(
                tool_id=tool_name,
                arguments=arguments,
            )
        )

        return self._serialize_tool_result(
            result
        )

    def _serialize_tool_definition(
        self,
        definition: ProjectToolDefinition,
    ) -> dict[str, Any]:
        """
        يحوّل تعريف الأداة الداخلي إلى شكل MCP العام.
        """
        return {
            "name": definition.tool_id,
            "description": definition.description,
            "inputSchema": definition.input_schema,
        }

    def _serialize_tool_result(
        self,
        result: ProjectToolResult,
    ) -> dict[str, Any]:
        """
        يحوّل نتيجة الحد إلى محتوى استجابة MCP.
        """
        payload = asdict(result)

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        payload,
                        ensure_ascii=False,
                    ),
                }
            ],
            "isError": not result.success,
        }

    def _error_response(
        self,
        message_id: Any,
        *,
        code: int,
        message: str,
    ) -> dict[str, Any]:
        """
        يبني استجابة JSON-RPC خطأ بالرمز والرسالة والبيانات المناسبة.
        """
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "error": {
                "code": code,
                "message": message,
            },
        }


async def run_stdio_server(
    server: ProjectMcpProtocolServer,
    *,
    stdin: TextIO = sys.stdin,
    stdout: TextIO = sys.stdout,
) -> None:
    """
    يشغل خادم MCP على stdin/stdout ويعالج الرسائل حتى انتهاء الإدخال.
    """
    while True:
        line = await asyncio.to_thread(
            stdin.readline
        )

        if line == "":
            break

        line = line.strip()

        if not line:
            continue

        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            response = server._error_response(
                None,
                code=-32700,
                message=str(exc),
            )
        else:
            response = await server.handle_message(
                message
            )

        if response is None:
            continue

        stdout.write(
            json.dumps(
                response,
                ensure_ascii=False,
            )
            + "\n"
        )
        stdout.flush()
