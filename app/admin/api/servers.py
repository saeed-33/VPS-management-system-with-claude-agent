from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from app.admin.dependencies import (
    get_server_service,
    get_ssh_test_service,
)
from app.admin.schemas.servers import (
    ServerCreateRequest,
    ServerResponse,
    ServerUpdateRequest,
    SSHTestResponse,
)
from app.admin.services.ssh_test_service import (
    SSHTestService,
)
from app.shared.dto.servers import (
    CreateServerDTO,
    UpdateServerDTO,
)
from app.shared.exceptions import (
    DuplicateServerError,
    ServerNotFoundError,
)
from app.shared.services.server_service import (
    ServerService,
)


router = APIRouter(
    prefix="/api/servers",
    tags=["servers"],
)


@router.get(
    "",
    response_model=list[ServerResponse],
)
def list_servers(
    service: ServerService = Depends(
        get_server_service
    ),
):
    return service.list_servers()


@router.get(
    "/{server_id}",
    response_model=ServerResponse,
)
def get_server(
    server_id: int,
    service: ServerService = Depends(
        get_server_service
    ),
):
    try:
        return service.get_server(server_id)
    except ServerNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=ServerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_server(
    payload: ServerCreateRequest,
    service: ServerService = Depends(
        get_server_service
    ),
):
    try:
        return service.create_server(
            CreateServerDTO(
                **payload.model_dump()
            )
        )
    except DuplicateServerError as exc:
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
    "/{server_id}",
    response_model=ServerResponse,
)
def update_server(
    server_id: int,
    payload: ServerUpdateRequest,
    service: ServerService = Depends(
        get_server_service
    ),
):
    try:
        return service.update_server(
            server_id,
            UpdateServerDTO(
                **payload.model_dump()
            ),
        )
    except ServerNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except DuplicateServerError as exc:
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
    "/{server_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_server(
    server_id: int,
    service: ServerService = Depends(
        get_server_service
    ),
) -> Response:
    try:
        service.delete_server(server_id)
    except ServerNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.post(
    "/{server_id}/test",
    response_model=SSHTestResponse,
)
async def test_ssh_connection(
    server_id: int,
    service: SSHTestService = Depends(
        get_ssh_test_service
    ),
):
    try:
        result = await service.test(server_id)
    except ServerNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return SSHTestResponse(
        success=result.success,
        message=result.message,
        hostname=result.hostname,
    )