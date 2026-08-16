"""
نقاط API لإدارة السيرفرات واختبار SSH.

تحول المسارات طلبات إنشاء وتعديل وحذف السيرفر إلى خدمة المجال، وتضيف تصنيف
السلامة للعرض وتعرض نتيجة اتصال SSH دون كشف تفاصيل التنفيذ الداخلية.
"""
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from app.interfaces.admin.dependencies import (
    get_server_service,
    get_ssh_test_service,
)
from app.interfaces.admin.schemas.servers import (
    ServerCreateRequest,
    ServerResponse,
    ServerUpdateRequest,
    SSHTestResponse,
)
from app.interfaces.admin.services.ssh_test_service import (
    SSHTestService,
)
from app.core.contracts.servers import (
    CreateServerDTO,
    UpdateServerDTO,
)
from app.core.exceptions import (
    DuplicateServerError,
    ServerNotFoundError,
)
from app.capabilities.monitoring.server_service import (
    ServerService,
)


router = APIRouter(
    prefix="/api/servers",
    tags=["servers"],
)


def _safety_designation(server) -> str:
    """
    يستنتج تصنيف سلامة السيرفر من وصفه لتمييز الإنتاج وبيئات الاختبار.
    """
    designation = str(getattr(server, "description", None) or "").casefold()
    if "safe-remediation-test" in designation and "non-production" in designation:
        return "safe_remediation_lab"
    if "non-production" in designation:
        return "non_production"
    if "production" in designation:
        return "production"
    return "unclassified"


def _server_response(server) -> ServerResponse:
    """
    يحوّل نموذج السيرفر إلى مخطط API ويضيف تصنيف السلامة المحسوب.
    """
    response = ServerResponse.model_validate(server)
    return response.model_copy(update={"safety_designation": _safety_designation(server)})


@router.get(
    "",
    response_model=list[ServerResponse],
)
def list_servers(
    service: ServerService = Depends(
        get_server_service
    ),
):
    """
    يعيد قائمة السيرفرات مع تصنيف السلامة لكل عنصر.
    """
    return [_server_response(item) for item in service.list_servers()]


@router.get(
    "/{server_id}",
    response_model=ServerResponse,
)
def get_server(
    server_id: int,
    service: ServerService = Depends(
        get_server_service
    ),
):
    """
    يجلب سيرفرًا بالمعرف ويحوّل غيابه إلى HTTP 404.
    """
    try:
        return _server_response(service.get_server(server_id))
    except ServerNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=ServerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_server(
    payload: ServerCreateRequest,
    service: ServerService = Depends(
        get_server_service
    ),
):
    """
    ينشئ سيرفرًا من طلب API ويحوّل تعارض الاسم أو المضيف إلى HTTP 409.
    """
    try:
        return _server_response(service.create_server(CreateServerDTO(**payload.model_dump())))
    except DuplicateServerError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{server_id}",
    response_model=ServerResponse,
)
def update_server(
    server_id: int,
    payload: ServerUpdateRequest,
    service: ServerService = Depends(
        get_server_service
    ),
):
    """
    يحدّث بيانات سيرفر موجود ويترجم أخطاء الغياب والتكرار إلى HTTP.
    """
    try:
        return _server_response(service.update_server(
            server_id,
            UpdateServerDTO(
                **payload.model_dump()
            ),
        ))
    except ServerNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except DuplicateServerError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{server_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_server(
    server_id: int,
    service: ServerService = Depends(
        get_server_service
    ),
) -> Response:
    """
    يحذف سيرفرًا ويعيد استجابة فارغة عند النجاح.
    """
    try:
        service.delete_server(server_id)
    except ServerNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.post(
    "/{server_id}/test",
    response_model=SSHTestResponse,
)
async def test_ssh_connection(
    server_id: int,
    service: SSHTestService = Depends(
        get_ssh_test_service
    ),
):
    """
    يشغل اختبار اتصال SSH لسيرفر ويعيد النتيجة الإدارية المنظمة.
    """
    try:
        result = await service.test(server_id)
    except ServerNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return SSHTestResponse(
        success=result.success,
        message=result.message,
        hostname=result.hostname,
    )
