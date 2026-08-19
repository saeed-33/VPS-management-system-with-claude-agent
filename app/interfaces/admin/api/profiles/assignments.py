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
from app.interfaces.admin.schemas.profiles.assign_profile_command_request import AssignProfileCommandRequest
from app.interfaces.admin.schemas.profiles.assign_server_profile_request import AssignServerProfileRequest
from app.interfaces.admin.schemas.profiles.monitoring_profile_create_request import MonitoringProfileCreateRequest
from app.interfaces.admin.schemas.profiles.monitoring_profile_response import MonitoringProfileResponse
from app.interfaces.admin.schemas.profiles.monitoring_profile_update_request import MonitoringProfileUpdateRequest
from app.interfaces.admin.schemas.profiles.profile_command_response import ProfileCommandResponse
from app.interfaces.admin.schemas.profiles.update_profile_command_request import UpdateProfileCommandRequest
from app.core.contracts.profiles.create_monitoring_profile_dto import CreateMonitoringProfileDTO
from app.core.contracts.profiles.update_monitoring_profile_dto import UpdateMonitoringProfileDTO
from app.core.exceptions.command_not_found_error import CommandNotFoundError
from app.core.exceptions.duplicate_monitoring_profile_error import DuplicateMonitoringProfileError
from app.core.exceptions.monitoring_profile_not_found_error import MonitoringProfileNotFoundError
from app.core.exceptions.profile_command_not_found_error import ProfileCommandNotFoundError
from app.core.exceptions.server_not_found_error import ServerNotFoundError
from app.capabilities.monitoring.profile_service import (
    MonitoringProfileService,
)


router = APIRouter(
    tags=["monitoring profiles"],
)

from .router import router


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
