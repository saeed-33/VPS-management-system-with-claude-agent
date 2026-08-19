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
