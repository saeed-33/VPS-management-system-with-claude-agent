"""
Endpoint من Admin API يحول HTTP إلى application service ويعيد schema للمشغل.

الموقع في المعمارية: HTTP interface / adapter.
يُستدعى بواسطة: عميل الإدارة عبر FastAPI.
يعتمد مباشرة على: app.interfaces.admin.dependencies، app.interfaces.admin.schemas.servers، app.interfaces.admin.services.ssh_test_service، app.core.contracts.servers، app.core.exceptions، app.capabilities.monitoring.server_service.
الحد المعماري: لا يضع business rules أو transaction logic.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
    """Read the persisted safe-target designation without hostname inference."""
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
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى _server_response؛ المدخلات المهمة: server.
    تعيد ServerResponse أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى list_servers؛ المدخلات المهمة: service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى get_server؛ المدخلات المهمة: server_id، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى create_server؛ المدخلات المهمة: payload، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى update_server؛ المدخلات المهمة: server_id، payload، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى delete_server؛ المدخلات المهمة: server_id، service.
    تعيد Response أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يتحقق من contract أو سلوك محدد عبر الحالة الاختبارية ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى test_ssh_connection؛ المدخلات المهمة: server_id، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    يفشل الاختبار عند خرق الـcontract، ولا يغير production state إلا إذا صمم لذلك.
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
