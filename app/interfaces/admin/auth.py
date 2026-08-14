from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from urllib.parse import parse_qs, quote, urlsplit

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.config import settings
from app.core.utils.datetime import utc_now
from app.infrastructure.database.models.admin_auth import (
    AdminAuthAuditEventModel,
    AdminSessionModel,
    AdminUserModel,
)
from app.infrastructure.database.session import SessionLocal


class AdminRole(StrEnum):
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


class AdminPermission(StrEnum):
    ADMIN_READ = "admin.read"
    SERVER_READ = "server.read"
    SERVER_WRITE = "server.write"
    PROFILE_READ = "profile.read"
    PROFILE_WRITE = "profile.write"
    MONITORING_READ = "monitoring.read"
    MONITORING_CONTROL = "monitoring.control"
    COMMAND_READ = "command.read"
    COMMAND_WRITE = "command.write"
    INVESTIGATION_READ = "investigation.read"
    REPORT_READ = "report.read"
    SPECIALIST_READ = "specialist.read"
    SPECIALIST_WRITE = "specialist.write"
    KNOWLEDGE_READ = "knowledge.read"
    KNOWLEDGE_WRITE = "knowledge.write"
    REMEDIATION_READ = "remediation.read"
    REMEDIATION_APPROVE = "remediation.approve"
    REMEDIATION_EXECUTE = "remediation.execute"
    REMEDIATION_ROLLBACK = "remediation.rollback"
    AUTONOMOUS_READ = "autonomous.read"
    AUTONOMOUS_POLICY_CREATE = "autonomous.policy.create"
    AUTONOMOUS_POLICY_UPDATE = "autonomous.policy.update"
    AUTONOMOUS_POLICY_ENABLE = "autonomous.policy.enable"
    AUTONOMOUS_POLICY_DISABLE = "autonomous.policy.disable"
    AUTONOMOUS_POLICY_SUSPEND = "autonomous.policy.suspend"
    AUTONOMOUS_POLICY_RESUME = "autonomous.policy.resume"
    AUDIT_READ = "audit.read"
    SYSTEM_READ = "system.read"
    SYSTEM_ADMIN = "system.admin"


_READ_PERMISSIONS = frozenset(
    {
        AdminPermission.ADMIN_READ,
        AdminPermission.SERVER_READ,
        AdminPermission.PROFILE_READ,
        AdminPermission.MONITORING_READ,
        AdminPermission.COMMAND_READ,
        AdminPermission.INVESTIGATION_READ,
        AdminPermission.REPORT_READ,
        AdminPermission.SPECIALIST_READ,
        AdminPermission.KNOWLEDGE_READ,
        AdminPermission.REMEDIATION_READ,
        AdminPermission.AUTONOMOUS_READ,
        AdminPermission.AUDIT_READ,
        AdminPermission.SYSTEM_READ,
    }
)

_OPERATOR_PERMISSIONS = frozenset(
    {
        AdminPermission.MONITORING_CONTROL,
        AdminPermission.REMEDIATION_APPROVE,
        AdminPermission.REMEDIATION_EXECUTE,
        AdminPermission.REMEDIATION_ROLLBACK,
    }
)

_ADMIN_PERMISSIONS = frozenset(
    {
        AdminPermission.SERVER_WRITE,
        AdminPermission.PROFILE_WRITE,
        AdminPermission.COMMAND_WRITE,
        AdminPermission.SPECIALIST_WRITE,
        AdminPermission.KNOWLEDGE_WRITE,
        AdminPermission.AUTONOMOUS_POLICY_CREATE,
        AdminPermission.AUTONOMOUS_POLICY_UPDATE,
        AdminPermission.AUTONOMOUS_POLICY_ENABLE,
        AdminPermission.AUTONOMOUS_POLICY_DISABLE,
        AdminPermission.AUTONOMOUS_POLICY_SUSPEND,
        AdminPermission.AUTONOMOUS_POLICY_RESUME,
        AdminPermission.SYSTEM_ADMIN,
    }
)

ROLE_PERMISSIONS: dict[AdminRole, frozenset[AdminPermission]] = {
    AdminRole.VIEWER: _READ_PERMISSIONS,
    AdminRole.OPERATOR: _READ_PERMISSIONS | _OPERATOR_PERMISSIONS,
    AdminRole.ADMIN: _READ_PERMISSIONS | _OPERATOR_PERMISSIONS | _ADMIN_PERMISSIONS,
}


@dataclass(frozen=True, slots=True)
class AdminPrincipal:
    """The request-scoped authenticated Admin identity."""

    user_id: int
    username: str
    role: AdminRole
    permissions: frozenset[AdminPermission]

    def can(self, permission: str | AdminPermission) -> bool:
        return AdminPermission(permission) in self.permissions


def principal_from_model(model: AdminUserModel) -> AdminPrincipal:
    role = AdminRole(model.role)
    return AdminPrincipal(
        user_id=model.id,
        username=model.username,
        role=role,
        permissions=ROLE_PERMISSIONS[role],
    )


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    n, r, p = 2**14, 8, 1
    digest = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=64
    )
    return f"scrypt${n}${r}${p}${_b64(salt)}${_b64(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt, expected = encoded.split("$", 5)
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=_unb64(salt),
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(_unb64(expected)),
        )
        return hmac.compare_digest(actual, _unb64(expected))
    except (TypeError, ValueError, OSError):
        return False


_DUMMY_PASSWORD_HASH = hash_password("admin-auth-dummy-password")
_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.@-]{2,119}$")


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def normalize_username(username: str) -> str:
    return str(username or "").strip().casefold()


def validate_admin_credentials(username: str, password: str) -> tuple[str, str]:
    normalized = normalize_username(username)
    if not _USERNAME_PATTERN.fullmatch(normalized):
        raise ValueError(
            "Username must be 3-120 characters and contain only letters, numbers, '.', '@', '_' or '-'."
        )
    if len(password) < 12 or not password.strip():
        raise ValueError("Password must contain at least 12 characters.")
    return normalized, password


class AdminAuthService:
    """Canonical persistence and cryptographic boundary for local Admin auth."""

    def __init__(
        self,
        *,
        session_factory: sessionmaker = SessionLocal,
        session_secret: str | None = None,
        session_ttl_seconds: int | None = None,
    ) -> None:
        self._session_factory = session_factory
        configured_secret = session_secret or settings.admin_session_secret
        self._session_secret = (
            configured_secret.encode("utf-8")
            if configured_secret
            else secrets.token_bytes(32)
        )
        self._session_ttl = timedelta(
            seconds=session_ttl_seconds or settings.admin_session_ttl_seconds
        )

    @property
    def cookie_name(self) -> str:
        return settings.admin_session_cookie_name

    @property
    def cookie_secure(self) -> bool:
        return settings.admin_session_secure

    @property
    def session_ttl_seconds(self) -> int:
        return int(self._session_ttl.total_seconds())

    def create_admin(self, *, username: str, password: str, role: str = "admin") -> AdminPrincipal:
        normalized, validated_password = validate_admin_credentials(username, password)
        normalized_role = AdminRole(role)
        with self._session_factory() as session:
            existing = session.scalar(
                select(AdminUserModel).where(AdminUserModel.username == normalized)
            )
            if existing is not None:
                raise ValueError("Admin username already exists.")
            model = AdminUserModel(
                username=normalized,
                password_hash=hash_password(validated_password),
                role=normalized_role.value,
                is_active=True,
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            principal = principal_from_model(model)
            self._write_audit(
                session,
                event_type="admin_created",
                principal=principal,
                success=True,
                metadata={"role": normalized_role.value},
            )
            session.commit()
            return principal

    def authenticate(self, *, username: str, password: str, request: Request) -> tuple[AdminPrincipal, str] | None:
        normalized = normalize_username(username)
        with self._session_factory() as session:
            model = session.scalar(
                select(AdminUserModel).where(AdminUserModel.username == normalized)
            )
            password_hash = model.password_hash if model else _DUMMY_PASSWORD_HASH
            valid = verify_password(password, password_hash)
            if model is None or not model.is_active or not valid:
                self._write_audit(
                    session,
                    event_type="login_failure",
                    username=normalized or None,
                    success=False,
                    request=request,
                )
                session.commit()
                return None

            now = utc_now()
            model.last_login_at = now
            raw_token = secrets.token_urlsafe(48)
            session.add(
                AdminSessionModel(
                    session_digest=self._digest(raw_token),
                    user_id=model.id,
                    expires_at=now + self._session_ttl,
                    user_agent=(request.headers.get("user-agent") or "")[:500] or None,
                    remote_addr=(request.client.host if request.client else None),
                )
            )
            principal = principal_from_model(model)
            self._write_audit(
                session,
                event_type="login_success",
                principal=principal,
                success=True,
                request=request,
            )
            session.commit()
            return principal, raw_token

    def authenticate_cookie(self, raw_token: str | None) -> AdminPrincipal | None:
        if not raw_token:
            return None
        now = utc_now()
        with self._session_factory() as session:
            session_model = session.scalar(
                select(AdminSessionModel).where(
                    AdminSessionModel.session_digest == self._digest(raw_token)
                )
            )
            if (
                session_model is None
                or session_model.revoked_at is not None
                or _utc(session_model.expires_at) <= now
            ):
                if session_model is not None and session_model.revoked_at is None:
                    session_model.revoked_at = now
                    session.commit()
                return None
            user = session.get(AdminUserModel, session_model.user_id)
            if user is None or not user.is_active:
                return None
            session_model.last_seen_at = now
            session.commit()
            return principal_from_model(user)

    def revoke_cookie(self, raw_token: str | None, *, request: Request) -> None:
        if not raw_token:
            return
        with self._session_factory() as session:
            session_model = session.scalar(
                select(AdminSessionModel).where(
                    AdminSessionModel.session_digest == self._digest(raw_token)
                )
            )
            principal = None
            if session_model is not None:
                user = session.get(AdminUserModel, session_model.user_id)
                principal = principal_from_model(user) if user else None
                session_model.revoked_at = utc_now()
            self._write_audit(
                session,
                event_type="logout",
                principal=principal,
                success=True,
                request=request,
            )
            session.commit()

    def csrf_token(self, raw_token: str | None) -> str:
        if not raw_token:
            return ""
        return hmac.new(
            self._session_secret,
            ("csrf:" + raw_token).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def csrf_valid(self, raw_token: str | None, supplied: str | None) -> bool:
        expected = self.csrf_token(raw_token)
        return bool(expected and supplied and hmac.compare_digest(expected, supplied))

    def record_event(
        self,
        *,
        event_type: str,
        principal: AdminPrincipal | None,
        request: Request | None = None,
        success: bool = True,
        metadata: dict | None = None,
    ) -> None:
        with self._session_factory() as session:
            self._write_audit(
                session,
                event_type=event_type,
                principal=principal,
                request=request,
                success=success,
                metadata=metadata,
            )
            session.commit()

    def list_audit_events(self, *, limit: int = 100) -> list[AdminAuthAuditEventModel]:
        """Return recent authentication and Admin security events for read-only audit views."""
        bounded_limit = max(1, min(int(limit), 500))
        with self._session_factory() as session:
            return list(
                session.scalars(
                    select(AdminAuthAuditEventModel)
                    .order_by(AdminAuthAuditEventModel.created_at.desc())
                    .limit(bounded_limit)
                )
            )

    @staticmethod
    def _write_audit(
        session,
        *,
        event_type: str,
        principal: AdminPrincipal | None = None,
        username: str | None = None,
        request: Request | None = None,
        success: bool = True,
        metadata: dict | None = None,
    ) -> None:
        session.add(
            AdminAuthAuditEventModel(
                event_id=secrets.token_hex(16),
                event_type=event_type,
                user_id=principal.user_id if principal else None,
                username=principal.username if principal else username,
                success=success,
                remote_addr=(
                    request.client.host if request and request.client else None
                ),
                user_agent=(
                    (request.headers.get("user-agent") or "")[:500] or None
                    if request
                    else None
                ),
                metadata_json=metadata or {},
            )
        )

    @staticmethod
    def _digest(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def safe_redirect_path(value: str | None, *, default: str = "/") -> str:
    candidate = str(value or "").strip()
    parsed = urlsplit(candidate)
    if not candidate.startswith("/") or candidate.startswith("//"):
        return default
    if parsed.scheme or parsed.netloc or "\\" in candidate:
        return default
    return candidate


def permission_for_api_request(
    method: str, path: str, *, payload: object | None = None
) -> AdminPermission:
    normalized = path.rstrip("/") or "/"
    if normalized.startswith("/api/servers"):
        if normalized.endswith("/test"):
            return AdminPermission.MONITORING_CONTROL
        if (
            method == "PATCH"
            and isinstance(payload, dict)
            and set(payload) == {"monitor_enabled"}
        ):
            return AdminPermission.MONITORING_CONTROL
        return AdminPermission.SERVER_READ if method == "GET" else AdminPermission.SERVER_WRITE
    if normalized.startswith("/api/commands"):
        return AdminPermission.COMMAND_READ if method == "GET" else AdminPermission.COMMAND_WRITE
    if normalized.startswith("/api/monitoring-profiles"):
        return AdminPermission.PROFILE_READ if method == "GET" else AdminPermission.PROFILE_WRITE
    if normalized.startswith("/api/reports"):
        return AdminPermission.REPORT_READ
    if normalized.startswith("/api/investigations"):
        return AdminPermission.INVESTIGATION_READ
    if normalized.startswith("/api/diagnostic-tools"):
        return AdminPermission.SYSTEM_READ
    if normalized.startswith("/api/specialists"):
        return AdminPermission.SPECIALIST_READ if method == "GET" else AdminPermission.SPECIALIST_WRITE
    if normalized.startswith("/api/knowledge-sources"):
        return AdminPermission.KNOWLEDGE_READ if method == "GET" else AdminPermission.KNOWLEDGE_WRITE
    if normalized.startswith("/api/agent-observability"):
        return AdminPermission.SYSTEM_READ
    if normalized == "/api/system/runtime":
        return AdminPermission.SYSTEM_READ
    if normalized.startswith("/api/remediation"):
        if method == "GET":
            return AdminPermission.REMEDIATION_READ
        if "/approval" in normalized:
            return AdminPermission.REMEDIATION_APPROVE
        if normalized.endswith("/execute"):
            return AdminPermission.REMEDIATION_EXECUTE
        if normalized.endswith("/rollback"):
            return AdminPermission.REMEDIATION_ROLLBACK
        return AdminPermission.REMEDIATION_APPROVE
    if normalized.startswith("/api/autonomous-remediation"):
        if method == "GET":
            if normalized.startswith("/api/autonomous-remediation/audit"):
                return AdminPermission.AUDIT_READ
            return AdminPermission.AUTONOMOUS_READ
        if normalized.endswith("/enable"):
            return AdminPermission.AUTONOMOUS_POLICY_ENABLE
        if normalized.endswith("/disable"):
            return AdminPermission.AUTONOMOUS_POLICY_DISABLE
        if normalized.endswith("/suspend"):
            return AdminPermission.AUTONOMOUS_POLICY_SUSPEND
        if normalized.endswith("/resume"):
            return AdminPermission.AUTONOMOUS_POLICY_RESUME
        if method == "POST":
            return AdminPermission.AUTONOMOUS_POLICY_CREATE
        return AdminPermission.AUTONOMOUS_POLICY_UPDATE
    return AdminPermission.SYSTEM_ADMIN if method != "GET" else AdminPermission.ADMIN_READ


class AdminAuthMiddleware(BaseHTTPMiddleware):
    """Central authentication, authorization, and CSRF enforcement boundary."""

    _PUBLIC_PREFIXES = (
        "/static/",
        "/docs",
        "/redoc",
        "/openapi.json",
    )

    def __init__(self, app, *, auth_service: AdminAuthService) -> None:
        super().__init__(app)
        self._auth_service = auth_service

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
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
        if path in {"/health", "/login"} or path.startswith("/static/"):
            return True
        if path == "/logout" and method == "GET":
            return False
        return any(
            path == prefix.rstrip("/") or path.startswith(prefix.rstrip("/") + "/")
            for prefix in cls._PUBLIC_PREFIXES
        )


def get_admin_principal(request: Request) -> AdminPrincipal:
    principal = getattr(request.state, "admin_user", None)
    if principal is None:
        raise PermissionError("Admin authentication required.")
    return principal
