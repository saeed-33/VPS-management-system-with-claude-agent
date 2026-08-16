"""
Endpoint من Admin API يحول HTTP إلى application service ويعيد schema للمشغل.

الموقع في المعمارية: HTTP interface / adapter.
يُستدعى بواسطة: عميل الإدارة عبر FastAPI.
يعتمد مباشرة على: app.interfaces.admin.dependencies، app.runtime.claude.supervisor، app.interfaces.mcp.registry، app.core.config، app.core.contracts.autonomous_remediation.
الحد المعماري: لا يضع business rules أو transaction logic.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from fastapi import APIRouter, Depends

from app.interfaces.admin.dependencies import (
    get_claude_supervisor,
    get_project_tool_boundary,
)
from app.runtime.claude.supervisor import (
    ClaudeSupervisor,
)
from app.interfaces.mcp.registry import (
    ProjectMcpToolBoundary,
)
from app.core.config import settings
from app.core.contracts.autonomous_remediation import (
    V1_AUTONOMOUS_ACTIONS,
    V1_AUTONOMOUS_RISK_CEILING,
)


router = APIRouter(
    tags=["system"],
)


@router.get(
    "/api/system/runtime",
)
async def get_runtime_overview(
    supervisor: ClaudeSupervisor = Depends(
        get_claude_supervisor
    ),
    tool_boundary: ProjectMcpToolBoundary = Depends(
        get_project_tool_boundary
    ),
) -> dict:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى get_runtime_overview؛ المدخلات المهمة: supervisor، tool_boundary.
    تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    tool_groups = (
        tool_boundary.list_tool_groups()
    )

    serialized_groups = [
        {
            "name": name,
            "tool_count": len(tools),
            "tools": [
                {
                    "tool_id": tool.tool_id,
                    "description": (
                        tool.description
                    ),
                    "read_only": tool.read_only,
                    "input_schema": (
                        tool.input_schema
                    ),
                }
                for tool in tools
            ],
        }
        for name, tools in tool_groups.items()
    ]

    return {
        "supervisor": supervisor.status,
        "claude_runtime": {
            "enabled": settings.claude_runtime_enabled,
            "executable": settings.claude_runtime_executable,
            "model": settings.effective_claude_runtime_model,
            "agent": settings.claude_runtime_agent,
            "max_turns": settings.claude_runtime_max_turns,
        },
        "ollama": {
            "provider": settings.llm_provider,
            "enabled": settings.llm_enabled,
            "base_url": settings.ollama_base_url,
            "model": settings.ollama_model,
        },
        "mcp": {
            "server_name": "vps",
            "configured": bool(serialized_groups),
            "tool_count": sum(
                group["tool_count"]
                for group in serialized_groups
            ),
        },
        "scheduler": {
            "state": supervisor.status.get(
                "state",
                "unknown",
            ),
            "polling_interval_seconds": (
                settings.monitor_polling_interval_seconds
            ),
        },
        "safety": {
            "automatic_remediation_allowed": settings.automatic_remediation_allowed,
            "v1_allowed_actions": sorted(V1_AUTONOMOUS_ACTIONS),
            "autonomous_max_risk": V1_AUTONOMOUS_RISK_CEILING,
            "phase6_sandbox_required": settings.phase6_require_wsl2,
            "phase6_attestation_configured": bool(settings.phase6_native_sandbox_attestation_file),
        },
        "admin_security": {
            "session_cookie_name": settings.admin_session_cookie_name,
            "session_ttl_seconds": settings.admin_session_ttl_seconds,
            "secure_cookie": settings.admin_session_secure,
            "csrf": "enabled",
        },
        "tool_count": sum(
            group["tool_count"]
            for group in serialized_groups
        ),
        "tool_groups": serialized_groups,
    }
