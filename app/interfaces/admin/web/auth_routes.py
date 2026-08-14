from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.interfaces.admin.auth import safe_redirect_path


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str | None = None):
    if getattr(request.state, "admin_user", None) is not None:
        return RedirectResponse(safe_redirect_path(next), status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"next_path": safe_redirect_path(next)},
    )


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str | None = Form(default=None),
):
    service = request.app.state.admin_auth_service
    result = service.authenticate(username=username, password=password, request=request)
    if result is None:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "next_path": safe_redirect_path(next),
                "error": "Invalid username or password.",
            },
            status_code=401,
        )

    _principal, raw_token = result
    response = RedirectResponse(safe_redirect_path(next), status_code=303)
    response.set_cookie(
        key=service.cookie_name,
        value=raw_token,
        max_age=service.session_ttl_seconds,
        httponly=True,
        secure=service.cookie_secure,
        samesite="lax",
        path="/",
    )
    return response


@router.post("/logout")
async def logout(request: Request):
    service = request.app.state.admin_auth_service
    service.revoke_cookie(request.cookies.get(service.cookie_name), request=request)
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(key=service.cookie_name, path="/")
    return response
