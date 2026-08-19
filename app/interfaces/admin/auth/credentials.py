"""تطبيع بيانات الاعتماد وتجزئة كلمات المرور."""
from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
from datetime import datetime, timezone

def _b64(value: bytes) -> str:
    """
    يرمز قيمة نصية بترميز Base64 آمن للاستخدام داخل الجلسة.
    """
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")
def _unb64(value: str) -> bytes:
    """
    يفك قيمة Base64 ويرفض المحتوى غير الصالح.
    """
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
def hash_password(password: str) -> str:
    """
    ينشئ تمثيلًا مملحًا ومشتقًا لكلمة المرور دون تخزينها بصورتها الأصلية.
    """
    salt = secrets.token_bytes(16)
    n, r, p = 2**14, 8, 1
    digest = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=64
    )
    return f"scrypt${n}${r}${p}${_b64(salt)}${_b64(digest)}"
def verify_password(password: str, encoded: str) -> bool:
    """
    يقارن كلمة المرور المقدمة بالتمثيل المشتق المخزن بطريقة آمنة.
    """
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
def _utc(value: datetime) -> datetime:
    """
    يعيد وقتًا UTC متوافقًا مع الحسابات الزمنية للجلسات والتدقيق.
    """
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
def normalize_username(username: str) -> str:
    """
    ينظف اسم المستخدم ويطبّع حالته قبل البحث أو الحفظ.
    """
    return str(username or "").strip().casefold()
def validate_admin_credentials(username: str, password: str) -> tuple[str, str]:
    """
    يتحقق من بيانات اعتماد الإدارة ويعيد المستخدم المقبول أو يرفضها.
    """
    normalized = normalize_username(username)
    if not _USERNAME_PATTERN.fullmatch(normalized):
        raise ValueError(
            "Username must be 3-120 characters and contain only letters, numbers, '.', '@', '_' or '-'."
        )
    if len(password) < 12 or not password.strip():
        raise ValueError("Password must contain at least 12 characters.")
    return normalized, password


_DUMMY_PASSWORD_HASH = hash_password("admin-auth-dummy-password")


_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.@-]{2,119}$")

