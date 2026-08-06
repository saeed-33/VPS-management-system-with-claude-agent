from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from app.admin.dependencies import (
    get_report_query_service,
)
from app.admin.schemas.reports import (
    PaginatedReportsResponse,
    ReportDetailsResponse,
)
from app.shared.exceptions import (
    ReportNotFoundError,
)
from app.shared.services.report_service import (
    ReportQueryService,
)


router = APIRouter(
    prefix="/api/reports",
    tags=["reports"],
)


@router.get(
    "",
    response_model=PaginatedReportsResponse,
)
def list_reports(
    service: Annotated[
        ReportQueryService,
        Depends(get_report_query_service),
    ],
    server_id: Annotated[
        int | None,
        Query(ge=1),
    ] = None,
    report_status: Annotated[
        str | None,
        Query(alias="status"),
    ] = None,
    page: Annotated[
        int,
        Query(ge=1),
    ] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=200),
    ] = 50,
) -> PaginatedReportsResponse:
    try:
        items, total = service.list_reports(
            server_id=server_id,
            status=report_status,
            page=page,
            page_size=page_size,
        )

        return PaginatedReportsResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.get(
    "/{report_id}",
    response_model=ReportDetailsResponse,
)
def get_report(
    report_id: int,
    service: Annotated[
        ReportQueryService,
        Depends(get_report_query_service),
    ],
) -> ReportDetailsResponse:
    try:
        return service.get_report(report_id)

    except ReportNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc