"""
Endpoint من Admin API يحول HTTP إلى application service ويعيد schema للمشغل.

الموقع في المعمارية: HTTP interface / adapter.
يُستدعى بواسطة: عميل الإدارة عبر FastAPI.
يعتمد مباشرة على: app.interfaces.admin.dependencies، app.runtime.claude.observability.
الحد المعماري: لا يضع business rules أو transaction logic.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from app.interfaces.admin.dependencies import (
    get_claude_agent_observability_service,
)
from app.runtime.claude.observability import (
    ClaudeAgentObservabilityService,
)


router = APIRouter(
    prefix="/api/agent-observability",
    tags=["agent-observability"],
)


@router.get("/jobs")
async def list_agent_job_traces(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    server_id: int | None = Query(
        default=None,
        ge=1,
    ),
    status: str | None = Query(
        default=None,
    ),
    service: ClaudeAgentObservabilityService = Depends(
        get_claude_agent_observability_service
    ),
) -> dict:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى list_agent_job_traces؛ المدخلات المهمة: limit، server_id، status، service.
    تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    traces = service.list_recent_traces(
        limit=limit,
        server_id=server_id,
        status=status,
    )

    return {
        "count": len(traces),
        "items": traces,
    }


@router.get("/jobs/{job_id}")
async def get_agent_job_trace(
    job_id: str,
    service: ClaudeAgentObservabilityService = Depends(
        get_claude_agent_observability_service
    ),
) -> dict:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى get_agent_job_trace؛ المدخلات المهمة: job_id، service.
    تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    trace = service.get_trace(job_id)

    if trace is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Agent job not found: "
                f"{job_id}"
            ),
        )

    return trace


@router.get("/summary")
async def get_agent_observability_summary(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    server_id: int | None = Query(
        default=None,
        ge=1,
    ),
    service: ClaudeAgentObservabilityService = Depends(
        get_claude_agent_observability_service
    ),
) -> dict:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى get_agent_observability_summary؛ المدخلات المهمة: limit، server_id، service.
    تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return service.summarize_recent(
        limit=limit,
        server_id=server_id,
    )
