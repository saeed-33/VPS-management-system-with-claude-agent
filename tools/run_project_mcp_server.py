"""
أداة CLI لإدارة database أو تشغيل MCP أو سيناريو خارجي.

الموقع في المعمارية: Operational tooling.
يُستدعى بواسطة: مشغل الأداة أو deployment workflow.
يعتمد مباشرة على: app.composition، app.interfaces.mcp.server.
الحد المعماري: لا يضيف endpoint أو capability تلقائيًا إلى التطبيق.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )

from app.composition import container
from app.interfaces.mcp.server import (
    ProjectMcpProtocolServer,
    run_stdio_server,
)


async def main() -> None:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Operational tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد None أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    await run_stdio_server(
        ProjectMcpProtocolServer(
            tool_boundary=(
                container.project_mcp_tool_boundary
            )
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
