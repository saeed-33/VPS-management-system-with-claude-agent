"""وسيط حماية واجهة الإدارة."""
from __future__ import annotations

import json
from urllib.parse import parse_qs, quote, urlsplit

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from .permissions import AdminPermission, permission_for_api_request
from .principal import AdminPrincipal
from .service import AdminAuthService


def safe_redirect_path(value: str | None, *, default: str = "/") -> str:
    """يتحقق من أن مسار إعادة التوجيه محلي وآمن."""
    candidate = str(value or "").strip()
    parsed = urlsplit(candidate)
    if not candidate.startswith("/") or candidate.startswith("//"):
        return default
    if parsed.scheme or parsed.netloc or "\\" in candidate:
        return default
    return candidate


class AdminAuthMiddleware(BaseHTTPMiddleware):
    """
    يفرض قواعد جلسة الإدارة على الطلبات ويمرر الهوية أو يعيد استجابة الحماية المناسبة.
    """

    _PUBLIC_PREFIXES = (
        "/static/",
        "/docs",
        "/redoc",
        "/openapi.json",
    )

    def __init__(self, app, *, auth_service: AdminAuthService) -> None:
        """
        يحفظ التطبيق وخدمة المصادقة وإعدادات مسارات الحماية للوسيط.
        """
        super().__init__(app)
        self._auth_service = auth_service

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        يفحص الطلب الإداري والجلسة وCSRF والصلاحية قبل تمريره أو إرجاع استجابة الرفض.
        """
        path = request.url.path
        if self._is_public(path, request.method):
            return await call_next(request)

        raw_token = request.cookies.get(self._auth_service.cookie_name)
        principal = self._auth_service.authenticate_cookie(raw_token)
        request.state.admin_user = principal
        request.state.admin_csrf_token = self._auth_service.csrf_token(raw_token)

        is_api = path.startswith("/api/")
        if principal is None:
            if is_api:
                return JSONResponse(
                    {"detail": "Authentication required."}, status_code=401
                )
            next_path = safe_redirect_path(path + ("?" + request.url.query if request.url.query else ""))
            return RedirectResponse(
                "/login?next=" + quote(next_path, safe=""),
                status_code=303,
            )

        payload = None
        if is_api and request.method == "PATCH" and path.startswith("/api/servers/"):
            try:
                payload = json.loads((await request.body()).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                payload = None
        required = (
            permission_for_api_request(request.method, path, payload=payload)
            if is_api
            else AdminPermission.ADMIN_READ
        )
        if not principal.can(required):
            self._auth_service.record_event(
                event_type="authorization_denied",
                principal=principal,
                request=request,
                success=False,
                metadata={"method": request.method, "path": path, "permission": required.value},
            )
            if is_api:
                return JSONResponse(
                    {"detail": "Admin permission required."}, status_code=403
                )
            return Response("Forbidden", status_code=403, media_type="text/plain")

        supplied_csrf = request.headers.get("x-csrf-token") or request.query_params.get("csrf_token")
        if supplied_csrf is None and request.headers.get("content-type", "").split(";", 1)[0].strip().lower() == "application/x-www-form-urlencoded":
            try:
                form_values = parse_qs((await request.body()).decode("utf-8"), keep_blank_values=True)
                supplied_csrf = form_values.get("csrf_token", [None])[0]
            except UnicodeDecodeError:
                supplied_csrf = None

        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and not self._auth_service.csrf_valid(
            raw_token, supplied_csrf
        ):
            return JSONResponse({"detail": "CSRF validation failed."}, status_code=403) if is_api else Response(
                "CSRF validation failed.", status_code=403, media_type="text/plain"
            )

        response = await call_next(request)
        if is_api and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            self._auth_service.record_event(
                event_type="admin_operation",
                principal=principal,
                request=request,
                success=response.status_code < 400,
                metadata={
                    "method": request.method,
                    "path": path,
                    "status_code": response.status_code,
                    "permission": required.value,
                },
            )
        return response

    @classmethod
    def _is_public(cls, path: str, method: str) -> bool:
        """
        يحدد ما إذا كان مسار الطلب مستثنى من المصادقة الإدارية.
        """
        if path in {"/health", "/login"} or path.startswith("/static/"):
            return True
        if path == "/logout" and method == "GET":
            return False
        return any(
            path == prefix.rstrip("/") or path.startswith(prefix.rstrip("/") + "/")
            for prefix in cls._PUBLIC_PREFIXES
        )


def get_admin_principal(request: Request) -> AdminPrincipal:
    """
    يعيد الهوية الإدارية الحالية من الطلب أو يرفع استجابة عدم المصادقة.
    """
    principal = getattr(request.state, "admin_user", None)
    if principal is None:
        raise PermissionError("Admin authentication required.")
    return principal

