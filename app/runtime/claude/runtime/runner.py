"""عقد تشغيل جلسة Claude."""
from typing import Protocol

from app.runtime.claude.models.raw_result import ClaudeRawResult
from app.runtime.claude.models.runtime_request import ClaudeRuntimeRequest

class ClaudeSessionRunner(Protocol):
    """
    عقد لتشغيل جلسة Claude أو إلغائها مع إعادة المخرج الخام.
    """
    async def run(
        self,
        request: ClaudeRuntimeRequest,
    ) -> ClaudeRawResult:
        """
        يشغل طلب جلسة Claude ويعيد المخرج الخام قبل تفسيره إلى نتيجة تشغيل.
        """

    async def cancel(
        self,
        identifier: str,
    ) -> None:
        """
        يلغي جلسة مرتبطة بمعرف مهمة حتى لا تستمر بعد انتهاء وقتها أو إلغاء الطلب.
        """
