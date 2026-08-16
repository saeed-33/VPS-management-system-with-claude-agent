"""
Endpoint من Admin API يحول HTTP إلى application service ويعيد schema للمشغل.

الموقع في المعمارية: HTTP interface / adapter.
يُستدعى بواسطة: عميل الإدارة عبر FastAPI.
يعتمد مباشرة على: app.interfaces.admin.dependencies، app.interfaces.admin.schemas.reports، app.interfaces.admin.services.report_pdf_service، app.infrastructure.database.repositories.analysis_repository، app.infrastructure.database.repositories.analysis_source_repository، app.core.exceptions.
الحد المعماري: لا يضع business rules أو transaction logic.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from fastapi.responses import Response

from app.interfaces.admin.dependencies import (
    get_analysis_repository,
    get_analysis_source_repository,
    get_report_pdf_service,
    get_report_query_service,
)
from app.interfaces.admin.schemas.reports import (
    PaginatedReportsResponse,
    ReportAnalysisResponse,
    ReportAnalysisSourcesResponse,
    ReportDetailsResponse,
)
from app.interfaces.admin.services.report_pdf_service import (
    ReportPdfService,
)
from app.infrastructure.database.repositories.analysis_repository import (
    AnalysisRepository,
)
from app.infrastructure.database.repositories.analysis_source_repository import (
    AnalysisSourceRepository,
)
from app.core.exceptions import (
    ReportNotFoundError,
)
from app.capabilities.monitoring.report_query_service import (
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
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى list_reports؛ المدخلات المهمة: service، server_id، report_status، page، page_size.
    تعيد PaginatedReportsResponse أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى get_report؛ المدخلات المهمة: report_id، service.
    تعيد ReportDetailsResponse أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    try:
        return service.get_report(report_id)

    except ReportNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/{report_id}/analysis",
    response_model=ReportAnalysisResponse,
)
def get_report_analysis(
    report_id: int,
    repository: Annotated[
        AnalysisRepository,
        Depends(get_analysis_repository),
    ],
):
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى get_report_analysis؛ المدخلات المهمة: report_id، repository.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    analysis = repository.get_by_report_id(
        report_id
    )

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No LLM analysis exists for "
                "this report."
            ),
        )

    return analysis


@router.get(
    "/{report_id}/analysis-sources",
    response_model=ReportAnalysisSourcesResponse,
)
def get_report_analysis_sources(
    report_id: int,
    analysis_repository: Annotated[
        AnalysisRepository,
        Depends(get_analysis_repository),
    ],
    source_repository: Annotated[
        AnalysisSourceRepository,
        Depends(get_analysis_source_repository),
    ],
) -> ReportAnalysisSourcesResponse:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى get_report_analysis_sources؛ المدخلات المهمة: report_id، analysis_repository، source_repository.
    تعيد ReportAnalysisSourcesResponse أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    analysis = analysis_repository.get_by_report_id(
        report_id
    )

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="No analysis exists for this report.",
        )

    return ReportAnalysisSourcesResponse(
        report_id=report_id,
        analysis_id=analysis.id,
        sources=source_repository.list_by_analysis_id(
            analysis.id
        ),
    )


@router.get(
    "/{report_id}/pdf",
    response_class=Response,
)
def export_report_pdf(
    report_id: int,
    report_service: Annotated[
        ReportQueryService,
        Depends(get_report_query_service),
    ],
    analysis_repository: Annotated[
        AnalysisRepository,
        Depends(get_analysis_repository),
    ],
    source_repository: Annotated[
        AnalysisSourceRepository,
        Depends(get_analysis_source_repository),
    ],
    pdf_service: Annotated[
        ReportPdfService,
        Depends(get_report_pdf_service),
    ],
) -> Response:
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى export_report_pdf؛ المدخلات المهمة: report_id، report_service، analysis_repository، source_repository، pdf_service.
    تعيد Response أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    try:
        report = report_service.get_report(report_id)
    except ReportNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    analysis = analysis_repository.get_by_report_id(
        report_id
    )

    sources = (
        source_repository.list_by_analysis_id(
            analysis.id
        )
        if analysis is not None
        else []
    )

    try:
        pdf_data = pdf_service.build(
            report=report,
            analysis=analysis,
            sources=sources,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {exc}",
        ) from exc

    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="report-{report_id}.pdf"'
            )
        },
    )


@router.get(
    "/{report_id}/analysis-summary",
)
def get_report_analysis_summary(
    report_id: int,
    repository: Annotated[
        AnalysisRepository,
        Depends(get_analysis_repository),
    ],
) -> dict:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى get_report_analysis_summary؛ المدخلات المهمة: report_id، repository.
    تعيد dict أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    analysis = repository.get_by_report_id(
        report_id
    )

    if analysis is None:
        return {
            "available": False,
            "status": None,
            "analysis_source": None,
            "llm_called": None,
            "reused_from_analysis_id": None,
        }

    return {
        "available": True,
        "status": analysis.status,
        "analysis_source": analysis.analysis_source,
        "llm_called": analysis.llm_called,
        "reused_from_analysis_id": (
            analysis.reused_from_analysis_id
        ),
    }
