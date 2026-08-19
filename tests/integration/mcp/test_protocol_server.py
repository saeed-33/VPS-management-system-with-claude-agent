"""Tests for test protocol server.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.interfaces.mcp.schemas، app.interfaces.mcp.server.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import asyncio
import json

from app.interfaces.mcp.schemas.definition import ProjectToolDefinition
from app.interfaces.mcp.schemas.result import ProjectToolResult
from app.interfaces.mcp.server import (
    ProjectMcpProtocolServer,
)


class ToolBoundary:
    """
    يمثل ToolBoundary جزءًا من طبقة Test suite.

    يجمع المسؤولية الظاهرة في هذا الملف ويستخدمه pytest أو أدوات acceptance. لا ينبغي أن يتولى
    تغيير production behavior خارج contract الذي تثبته أو الأداة التي يشغلها.
    """
    def list_tools(
        self,
    ) -> list[ProjectToolDefinition]:
        """
        يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى list_tools؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد list[ProjectToolDefinition] أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
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
        """
        ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

        تُستدعى عندما يصل المسار إلى execute؛ المدخلات المهمة: call.
        تعيد ProjectToolResult أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
        """
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
    """
    ينفذ مرحلة الأداة أو يحفظ نتيجة التقييم ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى run_message؛ المدخلات المهمة: message.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    server = ProjectMcpProtocolServer(
        tool_boundary=ToolBoundary()
    )

    return asyncio.run(
        server.handle_message(message)
    )


def test_mcp_initialize_exposes_tool_capability():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_mcp_initialize_exposes_tool_capability؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_mcp_tools_list_uses_project_tool_definitions؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_mcp_tools_call_returns_structured_project_result؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
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
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_mcp_unknown_method_returns_jsonrpc_error؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    response = run_message(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "unknown/method",
        }
    )

    assert response["error"]["code"] == -32601
