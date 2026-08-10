from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


WEB_DIRECTORY = Path(__file__).resolve().parent
TEMPLATES_DIRECTORY = (
    WEB_DIRECTORY / "templates"
)

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIRECTORY)
)

router = APIRouter(
    include_in_schema=False
)


@router.get(
    "/",
    response_class=HTMLResponse,
)
async def dashboard_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={},
    )


@router.get(
    "/servers",
    response_class=HTMLResponse,
)
async def servers_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="servers.html",
        context={},
    )


@router.get(
    "/commands",
    response_class=HTMLResponse,
)
async def commands_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="commands.html",
        context={},
    )


@router.get(
    "/investigations",
    response_class=HTMLResponse,
)
async def investigations_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="investigations.html",
        context={},
    )


@router.get(
    "/reports",
    response_class=HTMLResponse,
)
async def reports_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={},
    )
@router.get(
    "/monitoring-profiles",
    response_class=HTMLResponse,
)
async def monitoring_profiles_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="monitoring_profiles.html",
        context={},
    )
@router.get(
    "/investigations/{investigation_id}",
    response_class=HTMLResponse,
)
async def investigation_details_page(
    request: Request,
    investigation_id: str,
):
    return templates.TemplateResponse(
        request=request,
        name="investigation_details.html",
        context={
            "investigation_id": investigation_id,
        },
    )


@router.get(
    "/reports/{report_id}",
    response_class=HTMLResponse,
)
async def report_details_page(
    request: Request,
    report_id: int,
):
    return templates.TemplateResponse(
        request=request,
        name="report_details.html",
        context={
            "report_id": report_id,
        },
    )

@router.get(
    "/specialists",
    response_class=HTMLResponse,
)
async def specialists_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="specialists.html",
        context={},
    )

@router.get(
    "/knowledge-sources",
    response_class=HTMLResponse,
)
async def knowledge_sources_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="knowledge_sources.html",
        context={},
    )

