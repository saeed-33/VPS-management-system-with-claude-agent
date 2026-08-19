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
