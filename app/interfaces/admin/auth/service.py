"""خدمة جلسات ومصادقة الإدارة."""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import timedelta

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.utils.datetime import utc_now
from app.infrastructure.database.models.admin_auth.audit_event import AdminAuthAuditEventModel
from app.infrastructure.database.models.admin_auth.session import AdminSessionModel
from app.infrastructure.database.models.admin_auth.user import AdminUserModel
from app.infrastructure.database.session import SessionLocal

from .credentials import (
    _DUMMY_PASSWORD_HASH,
    _utc,
    hash_password,
    normalize_username,
    validate_admin_credentials,
    verify_password,
)
from .permissions import AdminRole
from .principal import AdminPrincipal, principal_from_model


class AdminAuthService:
    """
    يدير المستخدمين والجلسات وملفات الارتباط وCSRF وأحداث تدقيق المصادقة.
    """

    def __init__(
        self,
        *,
        session_factory: sessionmaker = SessionLocal,
        session_secret: str | None = None,
        session_ttl_seconds: int | None = None,
    ) -> None:
        """
        يحفظ التطبيق وخدمة المصادقة وإعدادات مسارات الحماية للوسيط.
        """
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
        """
        يعيد اسم ملف ارتباط جلسة الإدارة.
        """
        return settings.admin_session_cookie_name

    @property
    def cookie_secure(self) -> bool:
        """
        يعيد ما إذا كان ملف ارتباط الجلسة يجب أن يرسل عبر HTTPS فقط.
        """
        return settings.admin_session_secure

    @property
    def session_ttl_seconds(self) -> int:
        """
        يعيد مدة صلاحية جلسة الإدارة بالثواني.
        """
        return int(self._session_ttl.total_seconds())

    def create_admin(self, *, username: str, password: str, role: str = "admin") -> AdminPrincipal:
        """
        ينشئ مستخدمًا إداريًا مع الدور وكلمة المرور والصلاحيات المحددة.
        """
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
        """
        يتحقق من اسم المستخدم وكلمة المرور وينشئ جلسة إدارية عند النجاح.
        """
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
        """
        يقرأ ملف ارتباط الجلسة ويتحقق من صلاحيته ويعيد هوية المستخدم.
        """
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
        """
        يبطل جلسة الإدارة المرتبطة بملف الارتباط ويسجل عملية الإبطال.
        """
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
        """
        ينشئ أو يعيد رمز CSRF المرتبط بجلسة الإدارة.
        """
        if not raw_token:
            return ""
        return hmac.new(
            self._session_secret,
            ("csrf:" + raw_token).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def csrf_valid(self, raw_token: str | None, supplied: str | None) -> bool:
        """
        يتحقق من تطابق رمز CSRF مع جلسة الإدارة للطلب الحالي.
        """
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
        """
        يسجل حدث مصادقة أو إدارة في سجل التدقيق.
        """
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
        """
        يعيد أحداث تدقيق المصادقة وفق المرشحات الإدارية.
        """
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
        """
        يكتب سجل تدقيق المصادقة داخل جلسة قاعدة البيانات.
        """
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
        """
        ينشئ ملخصًا ثابتًا لقيمة حساسة بدل حفظها أو تسجيلها كما هي.
        """
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
