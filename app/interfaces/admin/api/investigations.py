"""
نقاط API لقراءة التحقيقات.

تقدم قوائم التحقيقات والتفاصيل والتحقيقات المرتبطة بتقرير مراقبة، مع ترك
التنفيذ والتجميع والحفظ لخدمات طبقة التحقيق.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.interfaces.admin.dependencies import get_investigation_read_service
from app.interfaces.admin.schemas.investigations.investigation_detail_response import InvestigationDetailResponse
from app.interfaces.admin.schemas.investigations.investigation_summary_response import InvestigationSummaryResponse
from app.capabilities.investigation.read_service import (
    InvestigationReadService,
)


router = APIRouter(tags=["investigations"])


@router.get(
    "/api/investigations",
    response_model=list[InvestigationSummaryResponse],
)
def list_investigations(
    limit: int = Query(default=100, ge=1, le=500),
    server_id: int | None = Query(default=None, ge=1),
    service: InvestigationReadService = Depends(
        get_investigation_read_service
    ),
):
    """
    يعيد قائمة التحقيقات مع مرشحات السيرفر والحالة والتاريخ.
    """
    return service.list_recent(
        limit=limit,
        server_id=server_id,
    )


@router.get(
    "/api/investigations/{investigation_id}",
    response_model=InvestigationDetailResponse,
)
def get_investigation(
    investigation_id: str,
    service: InvestigationReadService = Depends(
        get_investigation_read_service
    ),
):
    """
    يعيد تفاصيل تحقيق محدد أو HTTP 404 عند غيابه.
    """
    investigation_id = investigation_id.strip()

    if not investigation_id:
        raise HTTPException(
            status_code=422,
            detail="investigation_id must not be empty.",
        )

    result = service.get(investigation_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Investigation not found: {investigation_id}",
        )

    return result


@router.get(
    "/api/reports/{report_id}/investigations",
    response_model=list[InvestigationSummaryResponse],
)
def list_report_investigations(
    report_id: int,
    service: InvestigationReadService = Depends(
        get_investigation_read_service
    ),
):
    """
    يعرض التحقيقات المرتبطة بتقرير مراقبة محدد.
    """
    if report_id < 1:
        raise HTTPException(
            status_code=422,
            detail="report_id must be >= 1.",
        )

    return service.list_by_report_id(report_id)
