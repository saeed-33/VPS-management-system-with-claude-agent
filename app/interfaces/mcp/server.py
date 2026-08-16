"""
حد MCP يكشف Project capabilities لـClaude عبر أدوات typed ومتحقق منها.

الموقع في المعمارية: MCP capability boundary.
يُستدعى بواسطة: Claude أو خادم MCP.
يعتمد مباشرة على: app.interfaces.mcp.schemas.
الحد المعماري: MCP exposure ليس enforcement أمنيًا مستقلًا؛ التحقق الفعلي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
    يمثل ProjectMcpProtocolServer مسؤولية محددة داخل طبقة MCP capability boundary.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Claude أو خادم MCP
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        *,
        tool_boundary,
        server_name: str = "vps",
        version: str = "0.1.0",
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: tool_boundary، server_name، version.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._tool_boundary = tool_boundary
        self._server_name = server_name
        self._version = version

    async def handle_message(
        self,
        message: dict[str, Any],
    ) -> dict[str, Any] | None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى handle_message؛ المدخلات المهمة: message.
        تعيد dict[str, Any] | None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        # هذا هو protocol boundary: يترجم JSON-RPC ويستدعي registry، بينما
        # business result وauthorization يظلان داخل handlers/capabilities.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _initialize_result؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _tools_list_result؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _tools_call_result؛ المدخلات المهمة: params.
        تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _serialize_tool_definition؛ المدخلات المهمة: definition.
        تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _serialize_tool_result؛ المدخلات المهمة: result.
        تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

        تُستدعى عندما يصل workflow إلى _error_response؛ المدخلات المهمة: message_id، code، message.
        تعيد dict[str, Any] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة MCP capability boundary.

    تُستدعى عندما يصل workflow إلى run_stdio_server؛ المدخلات المهمة: server، stdin، stdout.
    تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
