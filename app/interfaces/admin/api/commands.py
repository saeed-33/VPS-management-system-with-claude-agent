"""
Endpoint من Admin API يحول HTTP إلى application service ويعيد schema للمشغل.

الموقع في المعمارية: HTTP interface / adapter.
يُستدعى بواسطة: عميل الإدارة عبر FastAPI.
يعتمد مباشرة على: app.interfaces.admin.dependencies، app.interfaces.admin.schemas.commands، app.core.contracts.commands، app.core.exceptions، app.capabilities.monitoring.command_service.
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
    get_command_service,
)
from app.interfaces.admin.schemas.commands import (
    AssignCommandRequest,
    CommandCreateRequest,
    CommandResponse,
    CommandUpdateRequest,
    ServerCommandAssignmentResponse,
    UpdateCommandAssignmentRequest,
)
from app.core.contracts.commands import (
    CreateCommandDTO,
    UpdateCommandDTO,
)
from app.core.exceptions import (
    CommandAlreadyAssignedError,
    CommandNotFoundError,
    DuplicateCommandError,
    ServerNotFoundError,
)
from app.capabilities.monitoring.command_service import (
    CommandService,
)


router = APIRouter(
    tags=["monitoring commands"],
)


@router.get(
    "/api/commands",
    response_model=list[CommandResponse],
)
def list_commands(
    service: CommandService = Depends(
        get_command_service
    ),
):
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى list_commands؛ المدخلات المهمة: service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    return service.list_commands()


@router.get(
    "/api/commands/{command_id}",
    response_model=CommandResponse,
)
def get_command(
    command_id: int,
    service: CommandService = Depends(
        get_command_service
    ),
):
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى get_command؛ المدخلات المهمة: command_id، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    try:
        return service.get_command(command_id)
    except CommandNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/api/commands",
    response_model=CommandResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_command(
    payload: CommandCreateRequest,
    service: CommandService = Depends(
        get_command_service
    ),
):
    """
    ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى create_command؛ المدخلات المهمة: payload، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    try:
        return service.create_command(
            CreateCommandDTO(
                **payload.model_dump()
            )
        )
    except DuplicateCommandError as exc:
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
    "/api/commands/{command_id}",
    response_model=CommandResponse,
)
def update_command(
    command_id: int,
    payload: CommandUpdateRequest,
    service: CommandService = Depends(
        get_command_service
    ),
):
    """
    يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى update_command؛ المدخلات المهمة: command_id، payload، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    try:
        return service.update_command(
            command_id,
            UpdateCommandDTO(
                **payload.model_dump()
            ),
        )
    except CommandNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except DuplicateCommandError as exc:
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
    "/api/commands/{command_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_command(
    command_id: int,
    service: CommandService = Depends(
        get_command_service
    ),
) -> Response:
    """
    يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى delete_command؛ المدخلات المهمة: command_id، service.
    تعيد Response أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    try:
        service.delete_command(command_id)
    except CommandNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

