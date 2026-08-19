"""
نقاط API لإدارة تعريفات الاختصاصيين.

توفر العمليات الإدارية قراءة وإنشاء وتعديل وتفعيل وحذف الاختصاصيين عبر خدمة
المجال مع الحفاظ على أخطاء المورد والتعارضات.
"""
from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

from app.interfaces.admin.dependencies import (
    get_specialist_definition_service,
)
from app.interfaces.admin.schemas.specialists.specialist_create_request import SpecialistCreateRequest
from app.interfaces.admin.schemas.specialists.specialist_enabled_request import SpecialistEnabledRequest
from app.interfaces.admin.schemas.specialists.specialist_response import SpecialistResponse
from app.interfaces.admin.schemas.specialists.specialist_update_request import SpecialistUpdateRequest
from app.core.contracts.specialists.create_specialist_definition_dto import CreateSpecialistDefinitionDTO
from app.core.contracts.specialists.update_specialist_definition_dto import UpdateSpecialistDefinitionDTO
from app.core.exceptions.duplicate_specialist_definition_error import DuplicateSpecialistDefinitionError
from app.core.exceptions.specialist_definition_not_found_error import SpecialistDefinitionNotFoundError
from app.capabilities.investigation.specialist_service import (
    SpecialistDefinitionService,
)


router = APIRouter(
    tags=["specialists"],
)


@router.get(
    "/api/specialists",
    response_model=list[SpecialistResponse],
)
def list_specialists(
    enabled_only: bool = Query(
        default=False,
    ),
    service: SpecialistDefinitionService = Depends(
        get_specialist_definition_service
    ),
):
    """
    يعرض تعريفات الاختصاصيين مع خيار الاقتصار على المفعلة.
    """
    return service.list_specialists(
        enabled_only=enabled_only
    )


@router.get(
    "/api/specialists/{specialist_id}",
    response_model=SpecialistResponse,
)
def get_specialist(
    specialist_id: int,
    service: SpecialistDefinitionService = Depends(
        get_specialist_definition_service
    ),
):
    """
    يجلب اختصاصيًا بالمعرف أو يعيد HTTP 404.
    """
    try:
        return service.get_specialist(
            specialist_id
        )
    except SpecialistDefinitionNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/api/specialists",
    response_model=SpecialistResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_specialist(
    payload: SpecialistCreateRequest,
    service: SpecialistDefinitionService = Depends(
        get_specialist_definition_service
    ),
):
    """
    ينشئ تعريف اختصاصي جديدًا ويعالج تعارض المعرف.
    """
    try:
        return service.create_specialist(
            CreateSpecialistDefinitionDTO(
                **payload.model_dump()
            )
        )
    except DuplicateSpecialistDefinitionError as exc:
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
    "/api/specialists/{specialist_id}",
    response_model=SpecialistResponse,
)
def update_specialist(
    specialist_id: int,
    payload: SpecialistUpdateRequest,
    service: SpecialistDefinitionService = Depends(
        get_specialist_definition_service
    ),
):
    """
    يحدّث تعريف اختصاصي مع ترجمة الغياب والتعارض إلى HTTP.
    """
    try:
        return service.update_specialist(
            specialist_id,
            UpdateSpecialistDefinitionDTO(
                **payload.model_dump()
            ),
        )
    except SpecialistDefinitionNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.put(
    "/api/specialists/{specialist_id}/enabled",
    response_model=SpecialistResponse,
)
def set_specialist_enabled(
    specialist_id: int,
    payload: SpecialistEnabledRequest,
    service: SpecialistDefinitionService = Depends(
        get_specialist_definition_service
    ),
):
    """
    يغير حالة تفعيل تعريف الاختصاصي.
    """
    try:
        return service.set_enabled(
            specialist_id,
            payload.enabled,
        )
    except SpecialistDefinitionNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.delete(
    "/api/specialists/{specialist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_specialist(
    specialist_id: int,
    service: SpecialistDefinitionService = Depends(
        get_specialist_definition_service
    ),
) -> Response:
    """
    يحذف تعريف اختصاصي ويعيد استجابة فارغة عند النجاح.
    """
    try:
        service.delete_specialist(
            specialist_id
        )
    except SpecialistDefinitionNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
