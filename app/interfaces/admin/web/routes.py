"""
جزء من واجهة الإدارة يعرّف route أو payload أو عرضًا للمشغل.

الموقع في المعمارية: Administration interface.
يُستدعى بواسطة: FastAPI أو متصفح الإدارة.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: العرض والتحقق الشكلي لا يمنحان صلاحية تنفيذ؛ authorization في الخدمة.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
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
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى dashboard_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى servers_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى commands_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى investigations_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى reports_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={},
    )


@router.get(
    "/system",
    response_class=HTMLResponse,
)
async def system_page(
    request: Request,
):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى system_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(
        request=request,
        name="system.html",
        context={},
    )
@router.get(
    "/monitoring-profiles",
    response_class=HTMLResponse,
)
async def monitoring_profiles_page(
    request: Request,
):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى monitoring_profiles_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى investigation_details_page؛ المدخلات المهمة: request، investigation_id.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى report_details_page؛ المدخلات المهمة: request، report_id.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى specialists_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
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
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى knowledge_sources_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(
        request=request,
        name="knowledge_sources.html",
        context={},
    )


@router.get(
    "/agent-runs",
    response_class=HTMLResponse,
)
async def agent_runs_page(
    request: Request,
):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى agent_runs_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(
        request=request,
        name="agent_runs.html",
        context={},
    )


@router.get(
    "/remediation",
    response_class=HTMLResponse,
)
async def remediation_page(
    request: Request,
):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى remediation_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(
        request=request,
        name="remediation.html",
        context={},
    )


@router.get(
    "/runtime-policies",
    response_class=HTMLResponse,
)
async def runtime_policies_page(
    request: Request,
):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى runtime_policies_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return RedirectResponse("/autonomous-runtime", status_code=307)


@router.get(
    "/autonomous-policies",
    response_class=HTMLResponse,
)
async def autonomous_policies_page(request: Request):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى autonomous_policies_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(request=request, name="autonomous_policies.html", context={})


@router.get(
    "/autonomous-candidates",
    response_class=HTMLResponse,
)
async def autonomous_candidates_page(request: Request):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى autonomous_candidates_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(request=request, name="autonomous_candidates.html", context={})


@router.get(
    "/autonomous-history",
    response_class=HTMLResponse,
)
async def autonomous_history_page(request: Request):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى autonomous_history_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(request=request, name="autonomous_history.html", context={})


@router.get(
    "/autonomous-decisions",
    response_class=HTMLResponse,
)
async def autonomous_decisions_page(request: Request):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى autonomous_decisions_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(request=request, name="autonomous_decisions.html", context={})


@router.get(
    "/autonomous-runtime",
    response_class=HTMLResponse,
)
async def autonomous_runtime_page(request: Request):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى autonomous_runtime_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(request=request, name="autonomous_runtime.html", context={})


@router.get(
    "/autonomous-reservations",
    response_class=HTMLResponse,
)
async def autonomous_reservations_page(request: Request):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى autonomous_reservations_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(request=request, name="autonomous_reservations.html", context={})


@router.get(
    "/autonomous-authorizations",
    response_class=HTMLResponse,
)
async def autonomous_authorizations_page(request: Request):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى autonomous_authorizations_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(request=request, name="autonomous_authorizations.html", context={})


@router.get(
    "/audit",
    response_class=HTMLResponse,
)
async def audit_page(request: Request):
    """
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Administration interface.

    تُستدعى عندما يصل workflow إلى audit_page؛ المدخلات المهمة: request.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return templates.TemplateResponse(request=request, name="audit.html", context={})
