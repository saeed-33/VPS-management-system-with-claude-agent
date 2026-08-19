"""
نقاط API لإدارة أوامر المراقبة.

تحول طلبات HTTP إلى عقود خدمة الأوامر وتترجم أخطاء التكرار والغياب والربط إلى
استجابات API واضحة، مع ترك التحقق والتنفيذ لخدمة المجال.
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
from app.interfaces.admin.schemas.commands.assign_command_request import AssignCommandRequest
from app.interfaces.admin.schemas.commands.command_create_request import CommandCreateRequest
from app.interfaces.admin.schemas.commands.command_response import CommandResponse
from app.interfaces.admin.schemas.commands.command_update_request import CommandUpdateRequest
from app.interfaces.admin.schemas.commands.server_command_assignment_response import ServerCommandAssignmentResponse
from app.interfaces.admin.schemas.commands.update_command_assignment_request import UpdateCommandAssignmentRequest
from app.core.contracts.commands.create_command_dto import CreateCommandDTO
from app.core.contracts.commands.update_command_dto import UpdateCommandDTO
from app.core.exceptions.command_already_assigned_error import CommandAlreadyAssignedError
from app.core.exceptions.command_not_found_error import CommandNotFoundError
from app.core.exceptions.duplicate_command_error import DuplicateCommandError
from app.core.exceptions.server_not_found_error import ServerNotFoundError
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
    يعيد جميع أوامر المراقبة المتاحة للإدارة.
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
    يجلب أمر مراقبة بالمعرف ويحوّل غيابه إلى HTTP 404.
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
    ينشئ أمر مراقبة من طلب API ويحوّل التعارض إلى HTTP 409.
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
    يحدّث أمر مراقبة موجودًا ويحوّل أخطاء الغياب أو التكرار إلى استجابات HTTP.
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
    يحذف أمر مراقبة ويعيد استجابة فارغة عند النجاح أو خطأ المورد عند الغياب.
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
