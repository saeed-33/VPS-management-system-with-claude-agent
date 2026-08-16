"""
نقاط API لإدارة ملفات المراقبة.

تدير هذه المسارات ملفات الأوامر وربطها بالسيرفرات، وتحوّل طلبات الإدارة إلى
عمليات خدمة مع الحفاظ على أخطاء الربط والموارد غير الموجودة.
"""
from dataclasses import asdict

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from app.interfaces.admin.dependencies import (
    get_monitoring_profile_service,
)
from app.interfaces.admin.schemas.profiles import (
    AssignProfileCommandRequest,
    AssignServerProfileRequest,
    MonitoringProfileCreateRequest,
    MonitoringProfileResponse,
    MonitoringProfileUpdateRequest,
    ProfileCommandResponse,
    UpdateProfileCommandRequest,
)
from app.core.contracts.profiles import (
    CreateMonitoringProfileDTO,
    UpdateMonitoringProfileDTO,
)
from app.core.exceptions import (
    CommandNotFoundError,
    DuplicateMonitoringProfileError,
    MonitoringProfileNotFoundError,
    ProfileCommandNotFoundError,
    ServerNotFoundError,
)
from app.capabilities.monitoring.profile_service import (
    MonitoringProfileService,
)


router = APIRouter(
    tags=["monitoring profiles"],
)


@router.get(
    "/api/monitoring-profiles",
    response_model=list[
        MonitoringProfileResponse
    ],
)
def list_profiles(
    service: MonitoringProfileService = Depends(
        get_monitoring_profile_service
    ),
):
    """
    يعيد ملفات المراقبة المتاحة للإدارة.
    """
    return service.list_profiles()


@router.get(
    "/api/monitoring-profiles/{profile_id}",
    response_model=MonitoringProfileResponse,
)
def get_profile(
    profile_id: int,
    service: MonitoringProfileService = Depends(
        get_monitoring_profile_service
    ),
):
    """
    يجلب ملف مراقبة بالمعرف ويحوّل غيابه إلى HTTP 404.
    """
    try:
        return service.get_profile(profile_id)
    except MonitoringProfileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/api/monitoring-profiles",
    response_model=MonitoringProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    payload: MonitoringProfileCreateRequest,
    service: MonitoringProfileService = Depends(
        get_monitoring_profile_service
    ),
):
    """
    ينشئ ملف مراقبة جديدًا من طلب API ويعالج تعارض الاسم.
    """
    try:
        return service.create_profile(
            CreateMonitoringProfileDTO(
                **payload.model_dump()
            )
        )
    except DuplicateMonitoringProfileError as exc:
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
    "/api/monitoring-profiles/{profile_id}",
    response_model=MonitoringProfileResponse,
)
def update_profile(
    profile_id: int,
    payload: MonitoringProfileUpdateRequest,
    service: MonitoringProfileService = Depends(
        get_monitoring_profile_service
    ),
):
    """
    يحدّث ملف مراقبة ويحوّل غياب الملف أو تعارض الاسم إلى استجابة مناسبة.
    """
    try:
        return service.update_profile(
            profile_id,
            UpdateMonitoringProfileDTO(
                **payload.model_dump()
            ),
        )
    except MonitoringProfileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except DuplicateMonitoringProfileError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.delete(
    "/api/monitoring-profiles/{profile_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_profile(
    profile_id: int,
    service: MonitoringProfileService = Depends(
        get_monitoring_profile_service
    ),
) -> Response:
    """
    يحذف ملف مراقبة ويرجع نجاحًا فارغًا أو خطأ المورد.
    """
    try:
        service.delete_profile(profile_id)
    except MonitoringProfileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.get(
    "/api/monitoring-profiles/"
    "{profile_id}/commands",
    response_model=list[ProfileCommandResponse],
)
def list_profile_commands(
    profile_id: int,
    service: MonitoringProfileService = Depends(
        get_monitoring_profile_service
    ),
):
    """
    يعرض الأوامر المرتبطة بملف مراقبة مع بيانات الترتيب والتفعيل.
    """
    try:
        rows = service.list_profile_commands(
            profile_id
        )
    except MonitoringProfileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return [
        ProfileCommandResponse(
            assignment_id=assignment.id,
            command_id=command.id,
            name=command.name,
            command=command.command,
            description=command.description,
            default_timeout_seconds=(
                command.timeout_seconds
            ),
            execution_order=(
                assignment.execution_order
            ),
            enabled=assignment.enabled,
            custom_timeout_seconds=(
                assignment.custom_timeout_seconds
            ),
        )
        for command, assignment in rows
    ]


@router.post(
    "/api/monitoring-profiles/"
    "{profile_id}/commands/{command_id}",
    response_model=ProfileCommandResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_command(
    profile_id: int,
    command_id: int,
    payload: AssignProfileCommandRequest,
    service: MonitoringProfileService = Depends(
        get_monitoring_profile_service
    ),
):
    """
    يربط أمرًا بملف مراقبة وفق طلب الإدارة.
    """
    try:
        assignment = service.assign_command(
            profile_id=profile_id,
            command_id=command_id,
            execution_order=(
                payload.execution_order
            ),
            enabled=payload.enabled,
            custom_timeout_seconds=(
                payload.custom_timeout_seconds
            ),
        )

        command = (
            service._command_repository.get_by_id(
                command_id
            )
        )

        return ProfileCommandResponse(
            assignment_id=assignment.id,
            command_id=command.id,
            name=command.name,
            command=command.command,
            description=command.description,
            default_timeout_seconds=(
                command.timeout_seconds
            ),
            execution_order=(
                assignment.execution_order
            ),
            enabled=assignment.enabled,
            custom_timeout_seconds=(
                assignment.custom_timeout_seconds
            ),
        )

    except (
        MonitoringProfileNotFoundError,
        CommandNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.patch(
    "/api/monitoring-profiles/"
    "{profile_id}/commands/{command_id}",
    response_model=ProfileCommandResponse,
)
def update_command_assignment(
    profile_id: int,
    command_id: int,
    payload: UpdateProfileCommandRequest,
    service: MonitoringProfileService = Depends(
        get_monitoring_profile_service
    ),
):
    """
    يعدّل إعدادات ربط أمر بملف مراقبة.
    """
    supplied_fields = payload.model_fields_set

    try:
        assignment = (
            service.update_command_assignment(
                profile_id=profile_id,
                command_id=command_id,
                execution_order=(
                    payload.execution_order
                ),
                enabled=payload.enabled,
                custom_timeout_seconds=(
                    payload.custom_timeout_seconds
                ),
                update_custom_timeout=(
                    "custom_timeout_seconds"
                    in supplied_fields
                ),
            )
        )

        command = (
            service._command_repository.get_by_id(
                command_id
            )
        )

        return ProfileCommandResponse(
            assignment_id=assignment.id,
            command_id=command.id,
            name=command.name,
            command=command.command,
            description=command.description,
            default_timeout_seconds=(
                command.timeout_seconds
            ),
            execution_order=(
                assignment.execution_order
            ),
            enabled=assignment.enabled,
            custom_timeout_seconds=(
                assignment.custom_timeout_seconds
            ),
        )

    except (
        MonitoringProfileNotFoundError,
        ProfileCommandNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.delete(
    "/api/monitoring-profiles/"
    "{profile_id}/commands/{command_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_command(
    profile_id: int,
    command_id: int,
    service: MonitoringProfileService = Depends(
        get_monitoring_profile_service
    ),
) -> Response:
    """
    يزيل ربط أمر من ملف مراقبة.
    """
    try:
        service.remove_command(
            profile_id=profile_id,
            command_id=command_id,
        )
    except ProfileCommandNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.put(
    "/api/servers/{server_id}/monitoring-profile",
    response_model=dict,
)
def assign_profile_to_server(
    server_id: int,
    payload: AssignServerProfileRequest,
    service: MonitoringProfileService = Depends(
        get_monitoring_profile_service
    ),
):
    """
    يربط ملف مراقبة بسيرفر ويعالج غياب أي من الموردين.
    """
    try:
        server = service.assign_profile_to_server(
            server_id=server_id,
            profile_id=payload.profile_id,
        )

        return {
            "server_id": server.id,
            "monitoring_profile_id": (
                server.monitoring_profile_id
            ),
        }

    except (
        ServerNotFoundError,
        MonitoringProfileNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc