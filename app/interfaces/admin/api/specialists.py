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
from app.interfaces.admin.schemas.specialists import (
    SpecialistCreateRequest,
    SpecialistEnabledRequest,
    SpecialistResponse,
    SpecialistUpdateRequest,
)
from app.core.contracts.specialists import (
    CreateSpecialistDefinitionDTO,
    UpdateSpecialistDefinitionDTO,
)
from app.core.exceptions import (
    DuplicateSpecialistDefinitionError,
    SpecialistDefinitionNotFoundError,
)
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
