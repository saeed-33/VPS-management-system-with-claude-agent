"""
Endpoint من Admin API يحول HTTP إلى application service ويعيد schema للمشغل.

الموقع في المعمارية: HTTP interface / adapter.
يُستدعى بواسطة: عميل الإدارة عبر FastAPI.
يعتمد مباشرة على: app.interfaces.admin.dependencies، app.interfaces.admin.schemas.profiles، app.core.contracts.profiles، app.core.exceptions، app.capabilities.monitoring.profile_service.
الحد المعماري: لا يضع business rules أو transaction logic.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
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
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى list_profiles؛ المدخلات المهمة: service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى get_profile؛ المدخلات المهمة: profile_id، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    ينشئ أو يحفظ نتيجة العملية في الطبقة المالكة للبيانات ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى create_profile؛ المدخلات المهمة: payload، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى update_profile؛ المدخلات المهمة: profile_id، payload، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى delete_profile؛ المدخلات المهمة: profile_id، service.
    تعيد Response أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى list_profile_commands؛ المدخلات المهمة: profile_id، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى assign_command؛ المدخلات المهمة: profile_id، command_id، payload، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يحدّث حالة أو إعدادًا بعد تطبيق التحقق الموجود ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى update_command_assignment؛ المدخلات المهمة: profile_id، command_id، payload، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    يحذف أو يزيل الكيان وفق contract الطبقة ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى remove_command؛ المدخلات المهمة: profile_id، command_id، service.
    تعيد Response أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
    ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى assign_profile_to_server؛ المدخلات المهمة: server_id، payload، service.
    تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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