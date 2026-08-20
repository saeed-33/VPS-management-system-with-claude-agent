"""منفذ أو عقد من مكونات تنفيذ المعالجة."""
from __future__ import annotations

class FallbackVerificationRunner:
    """
    يمثل متحققاً احتياطياً يبلغ عن عدم إمكانية التحقق.
    """
    def verify(self, **_kwargs) -> tuple[bool, dict]:
        """
        يعيد نتيجة فشل توضّح أن التحقق غير متاح.
        """
        return False, {"error": "safe_verification_runner_not_configured"}
