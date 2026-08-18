"""
تنسيق دورة جلسة Claude من الطلب حتى النتيجة المحفوظة.

يفرض محرك التشغيل حدود الوقت وصلاحية الأدوات، يلغي الجلسة عند المهلة، يفسر
المخرج المنظم، ويحوّل كل فشل إلى نتيجة تشغيل قابلة للتسجيل.
"""
from __future__ import annotations

import asyncio
from typing import Protocol

from app.runtime.claude.exceptions import (
    ClaudeRuntimeError,
    ClaudeStructuredOutputError,
    ClaudeToolAccessError,
    describe_exception,
)
from app.runtime.claude.models import (
    ClaudeJobStatus,
    ClaudeRawResult,
    ClaudeRuntimeRequest,
    ClaudeRuntimeResult,
)
from app.runtime.claude.result_parser import (
    ClaudeStructuredResultParser,
)


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


class ClaudeRuntimeAdapter:
    """
    محول يطبق حدود الأمان والوقت ويفسر مخرج الجلسة إلى نتيجة قابلة للحفظ.
    """
    def __init__(
        self,
        *,
        runner: ClaudeSessionRunner,
        parser: ClaudeStructuredResultParser | None = None,
        operational_tools_enabled: bool = False,
    ) -> None:
        """
        يجهز مشغل الجلسة ومحلل النتائج وعلم السماح بالأدوات التشغيلية.
        """
        self._runner = runner
        self._parser = (
            parser
            if parser is not None
            else ClaudeStructuredResultParser()
        )
        self._operational_tools_enabled = (
            operational_tools_enabled
        )

    async def execute(
        self,
        request: ClaudeRuntimeRequest,
    ) -> ClaudeRuntimeResult:
        """
        يشغل الجلسة ضمن المهلة، يلغيها عند التأخر، يفسر مخرجها، ويعيد نجاحًا أو فشلًا موحدًا.
        """
        try:
            self._validate_tool_access(
                request
            )

        except ClaudeToolAccessError as exc:
            return self._failure(
                request,
                error_code="tool_access_disabled",
                error_message=str(exc),
            )

        try:
            # يفصل هذا المسار جلسة Claude عن تشغيل العملية؛ يحدد المزود طريقة
            # الجلسة، بينما تفرض هذه الخدمة المهلة والإلغاء والتحقق.
            raw_result = await asyncio.wait_for(
                self._runner.run(
                    request
                ),
                timeout=request.timeout_seconds,
            )

        except TimeoutError:
            await self._best_effort_cancel(
                request.job_id
            )
            return self._failure(
                request,
                status=ClaudeJobStatus.TIMED_OUT,
                error_code="timed_out",
                error_message=(
                    "Claude runtime exceeded "
                    f"{request.timeout_seconds} seconds."
                ),
            )

        except ClaudeRuntimeError as exc:
            return self._failure(
                request,
                error_code="runtime_error",
                error_message=describe_exception(
                    exc,
                    fallback=(
                        "Claude runtime failed without diagnostic output."
                    ),
                ),
            )

        except Exception as exc:
            return self._failure(
                request,
                error_code="unexpected_error",
                error_message=describe_exception(
                    exc,
                    fallback=(
                        "Unexpected Claude runtime failure without "
                        "diagnostic output."
                    ),
                ),
            )

        try:
            structured_output = (
                self._parser.parse(
                    raw_result.content
                )
            )

        except ClaudeStructuredOutputError as exc:
            return self._failure(
                request,
                session_id=raw_result.session_id,
                error_code="invalid_structured_output",
                error_message=str(exc),
                turn_count=raw_result.turn_count,
                tool_call_count=(
                    raw_result.tool_call_count
                ),
                usage_metadata=(
                    raw_result.usage_metadata
                ),
            )

        if (
            structured_output.status
            == ClaudeJobStatus.COMPLETED
        ):
            return ClaudeRuntimeResult(
                job_id=request.job_id,
                job_type=request.job_type,
                status=ClaudeJobStatus.COMPLETED,
                session_id=raw_result.session_id,
                structured_output=structured_output,
                turn_count=raw_result.turn_count,
                tool_call_count=(
                    raw_result.tool_call_count
                ),
                usage_metadata=(
                    raw_result.usage_metadata
                ),
            )

        return self._failure(
            request,
            status=structured_output.status,
            session_id=raw_result.session_id,
            structured_output=structured_output,
            error_code="claude_reported_failure",
            error_message=structured_output.summary,
            turn_count=raw_result.turn_count,
            tool_call_count=raw_result.tool_call_count,
            usage_metadata=raw_result.usage_metadata,
        )

    async def _best_effort_cancel(
        self,
        identifier: str,
    ) -> None:
        """
        يحاول إيقاف الجلسة بعد المهلة دون أن يخفي نتيجة المهلة إذا تعذر الإلغاء.
        """
        try:
            await self._runner.cancel(
                identifier
            )
        except Exception:
            # تبقى المهلة هي النتيجة الأساسية عندما لا تنتهي الجلسة في وقتها.
            pass

    def _validate_tool_access(
        self,
        request: ClaudeRuntimeRequest,
    ) -> None:
        """
        يرفض الطلب الذي يحتوي أدوات تشغيلية عندما لا يكون runtime مفعّلًا للوصول إليها.
        """
        if (
            request.allowed_tools
            and not self._operational_tools_enabled
        ):
            raise ClaudeToolAccessError(
                "Operational tool access is not enabled "
                "for this Claude runtime adapter."
            )

    def _failure(
        self,
        request: ClaudeRuntimeRequest,
        *,
        status: ClaudeJobStatus = ClaudeJobStatus.FAILED,
        session_id: str | None = None,
        structured_output=None,
        error_code: str,
        error_message: str,
        turn_count: int = 0,
        tool_call_count: int = 0,
        usage_metadata: dict | None = None,
    ) -> ClaudeRuntimeResult:
        """
        ينشئ نتيجة فشل موحدة تحفظ الحالة والسبب والمعرف والعدادات المتاحة.
        """
        return ClaudeRuntimeResult(
            job_id=request.job_id,
            job_type=request.job_type,
            status=status,
            session_id=session_id,
            structured_output=structured_output,
            error_code=error_code,
            error_message=error_message,
            turn_count=turn_count,
            tool_call_count=tool_call_count,
            usage_metadata=(
                usage_metadata
                if usage_metadata is not None
                else {}
            ),
        )
