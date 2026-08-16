"""
جزء من Claude Runtime لبناء العملية أو تشغيل الجلسة أو قراءة stream أو تسجيل job.

الموقع في المعمارية: Claude supervisory runtime.
يُستدعى بواسطة: composition أو Scheduler.
يعتمد مباشرة على: app.runtime.claude.exceptions، app.runtime.claude.models، app.runtime.claude.result_parser.
الحد المعماري: Claude/Ollama للـreasoning/model؛ policy والحفظ والتنفيذ الحتمي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

import asyncio
from typing import Protocol

from app.runtime.claude.exceptions import (
    ClaudeRuntimeError,
    ClaudeStructuredOutputError,
    ClaudeToolAccessError,
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
    يمثل ClaudeSessionRunner مسؤولية محددة داخل طبقة Claude supervisory runtime.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه composition أو Scheduler
    ويعتمد على Protocol وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    async def run(
        self,
        request: ClaudeRuntimeRequest,
    ) -> ClaudeRawResult:
        """Run one bounded Claude session and return raw output."""

    async def cancel(
        self,
        identifier: str,
    ) -> None:
        """Best-effort cancellation by current runtime identifier."""


class ClaudeRuntimeAdapter:
    """
    يمثل ClaudeRuntimeAdapter مسؤولية محددة داخل طبقة Claude supervisory runtime.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه composition أو Scheduler
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        *,
        runner: ClaudeSessionRunner,
        parser: ClaudeStructuredResultParser | None = None,
        operational_tools_enabled: bool = False,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: runner، parser، operational_tools_enabled.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يشغّل workflow هذه الطبقة ويربط مراحله ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى execute؛ المدخلات المهمة: request.
        تعيد ClaudeRuntimeResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
            # يفصل adapter بين Claude orchestration وprocess runner؛ Ollama
            # يحدد provider، بينما timeout/cancellation والتحقق حتمية هنا.
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
                error_message=str(exc),
            )

        except Exception as exc:
            return self._failure(
                request,
                error_code="unexpected_error",
                error_message=str(exc),
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى _best_effort_cancel؛ المدخلات المهمة: identifier.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        try:
            await self._runner.cancel(
                identifier
            )
        except Exception:
            # The primary controlled outcome remains timeout.
            pass

    def _validate_tool_access(
        self,
        request: ClaudeRuntimeRequest,
    ) -> None:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى _validate_tool_access؛ المدخلات المهمة: request.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى _failure؛ المدخلات المهمة: request، status، session_id، structured_output، error_code، error_message.
        تعيد ClaudeRuntimeResult أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
