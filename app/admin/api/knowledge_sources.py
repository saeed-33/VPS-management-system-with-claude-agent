from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

from app.admin.dependencies import (
    get_knowledge_source_service,
)
from app.admin.schemas.knowledge_sources import (
    KnowledgeSourceCreateRequest,
    KnowledgeSourceEnabledRequest,
    KnowledgeSourceResponse,
    KnowledgeSourceUpdateRequest,
)
from app.shared.dto.knowledge_sources import (
    CreateKnowledgeSourceDTO,
    UpdateKnowledgeSourceDTO,
)
from app.shared.services.knowledge_source_service import (
    KnowledgeSourceService,
)


router = APIRouter(
    tags=["knowledge-sources"],
)


@router.get(
    "/api/knowledge-sources",
    response_model=list[
        KnowledgeSourceResponse
    ],
)
def list_knowledge_sources(
    enabled_only: bool = Query(
        default=False
    ),
    service: KnowledgeSourceService = Depends(
        get_knowledge_source_service
    ),
):
    return service.list_sources(
        enabled_only=enabled_only
    )


@router.get(
    "/api/knowledge-sources/{source_id}",
    response_model=KnowledgeSourceResponse,
)
def get_knowledge_source(
    source_id: int,
    service: KnowledgeSourceService = Depends(
        get_knowledge_source_service
    ),
):
    try:
        return service.get_source(
            source_id
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/api/knowledge-sources",
    response_model=KnowledgeSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_source(
    payload: KnowledgeSourceCreateRequest,
    service: KnowledgeSourceService = Depends(
        get_knowledge_source_service
    ),
):
    try:
        return service.create_source(
            CreateKnowledgeSourceDTO(
                slug=payload.slug,
                name=payload.name,
                description=(
                    payload.description
                ),
                source_type=(
                    payload.source_type
                ),
                source_uri=payload.source_uri,
                inline_content=(
                    payload.inline_content
                ),
                enabled=payload.enabled,
                domains=tuple(
                    payload.domains
                ),
                specialist_slugs=tuple(
                    payload.specialist_slugs
                ),
                tags=tuple(payload.tags),
                priority=payload.priority,
                metadata=payload.metadata,
            )
        )
    except ValueError as exc:
        detail = str(exc)
        status_code = (
            409
            if "already exists"
            in detail
            else 422
        )
        raise HTTPException(
            status_code=status_code,
            detail=detail,
        ) from exc


@router.patch(
    "/api/knowledge-sources/{source_id}",
    response_model=KnowledgeSourceResponse,
)
def update_knowledge_source(
    source_id: int,
    payload: KnowledgeSourceUpdateRequest,
    service: KnowledgeSourceService = Depends(
        get_knowledge_source_service
    ),
):
    try:
        return service.update_source(
            source_id,
            UpdateKnowledgeSourceDTO(
                name=payload.name,
                description=(
                    payload.description
                ),
                source_type=(
                    payload.source_type
                ),
                source_uri=(
                    payload.source_uri
                ),
                inline_content=(
                    payload.inline_content
                ),
                enabled=payload.enabled,
                domains=(
                    tuple(payload.domains)
                    if payload.domains
                    is not None
                    else None
                ),
                specialist_slugs=(
                    tuple(
                        payload
                        .specialist_slugs
                    )
                    if payload
                    .specialist_slugs
                    is not None
                    else None
                ),
                tags=(
                    tuple(payload.tags)
                    if payload.tags
                    is not None
                    else None
                ),
                priority=payload.priority,
                metadata=payload.metadata,
            ),
        )
    except LookupError as exc:
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
    "/api/knowledge-sources/{source_id}/enabled",
    response_model=KnowledgeSourceResponse,
)
def set_knowledge_source_enabled(
    source_id: int,
    payload: KnowledgeSourceEnabledRequest,
    service: KnowledgeSourceService = Depends(
        get_knowledge_source_service
    ),
):
    try:
        return service.set_enabled(
            source_id,
            payload.enabled,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.delete(
    "/api/knowledge-sources/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_knowledge_source(
    source_id: int,
    service: KnowledgeSourceService = Depends(
        get_knowledge_source_service
    ),
) -> Response:
    try:
        service.delete_source(
            source_id
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
