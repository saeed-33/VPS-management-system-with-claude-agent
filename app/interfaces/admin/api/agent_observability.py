"""
نقاط API لمراقبة آثار وظائف وكيل Claude.

تستقبل هذه المسارات مرشحات التتبع وتعيد تفاصيل الوظائف وملخصات المراقبة عبر
خدمة الرصد، دون أن تنفذ الوظيفة نفسها أو تغير حالة الوكيل.
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
from app.runtime.claude.observability.observability import ClaudeAgentObservabilityService


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
    يعيد آثار وظائف الوكيل وفق حد النتائج والسيرفر والحالة المطلوبة.
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
    يعيد تفاصيل أثر وظيفة وكيل محددة أو استجابة عدم العثور عليها.
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
    يعيد ملخصًا تجميعيًا لمراقبة وظائف الوكيل ضمن المرشحات المطلوبة.
    """
    return service.summarize_recent(
        limit=limit,
        server_id=server_id,
    )
