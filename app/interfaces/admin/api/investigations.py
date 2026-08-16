"""
Endpoint من Admin API يحول HTTP إلى application service ويعيد schema للمشغل.

الموقع في المعمارية: HTTP interface / adapter.
يُستدعى بواسطة: عميل الإدارة عبر FastAPI.
يعتمد مباشرة على: app.interfaces.admin.dependencies، app.interfaces.admin.schemas.investigations، app.capabilities.investigation.read_service.
الحد المعماري: لا يضع business rules أو transaction logic.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.interfaces.admin.dependencies import get_investigation_read_service
from app.interfaces.admin.schemas.investigations import (
    InvestigationDetailResponse,
    InvestigationSummaryResponse,
)
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
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى list_investigations؛ المدخلات المهمة: limit، server_id، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى get_investigation؛ المدخلات المهمة: investigation_id، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى list_report_investigations؛ المدخلات المهمة: report_id، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    if report_id < 1:
        raise HTTPException(
            status_code=422,
            detail="report_id must be >= 1.",
        )

    return service.list_by_report_id(report_id)
