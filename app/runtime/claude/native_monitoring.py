"""
تشغيل دورة المراقبة الفعلية لسيرفر عبر جلسة Claude.

ينشئ العامل طلبًا يفرض تسلسل أدوات المراقبة والتحليل والتحقيق، يحفظ انتقالات
المهمة، ثم يعيد نتيجة موثقة أو يرفع فشلًا مضبوطًا عند عدم اكتمال الدورة.
"""
from __future__ import annotations

import asyncio
from dataclasses import replace
import logging
from uuid import uuid4

from app.runtime.claude.exceptions import (
    ClaudeRuntimeError,
    describe_exception,
)
from app.runtime.claude.job_service import ClaudeAgentJobService
from app.runtime.claude.models import (
    ClaudeJobStatus,
    ClaudeRuntimeResult,
    ClaudeRuntimeRequest,
)
from app.runtime.claude.runtime import ClaudeRuntimeAdapter


logger = logging.getLogger(__name__)


SERVER_SUPERVISOR_ALLOWED_TOOLS = (
    "mcp__vps__get_server_context",
    "mcp__vps__get_monitoring_profile",
    "mcp__vps__run_monitoring",
    "mcp__vps__get_latest_report",
    "mcp__vps__get_report",
    "mcp__vps__find_exact_report_match",
    "mcp__vps__get_top_similar_reports",
    "mcp__vps__analyze_report",
    "mcp__vps__get_analysis",
    "mcp__vps__start_investigation",
    "mcp__vps__get_investigation",
    "mcp__vps__get_investigation_status",
    "mcp__vps__get_evidence",
    "mcp__vps__get_available_specialists",
    "mcp__vps__get_specialist_definition",
    "mcp__vps__run_specialist",
    "mcp__vps__propose_remediation",
    "mcp__vps__attempt_autonomous_remediation",
    "Agent(specialist-worker)",
)


class ClaudeNativeMonitoringRunner:
    """
    عامل يطلق دورة مراقبة حقيقية ويضمن تسجيلها من إنشاء المهمة حتى اكتمال النتيجة.
    """

    def __init__(
        self,
        *,
        runtime_adapter: ClaudeRuntimeAdapter,
        agent_job_service: ClaudeAgentJobService,
        timeout_seconds: float,
        max_turns: int,
    ) -> None:
        """
        يجهز مشغل المراقبة بمحرك الجلسة وخدمة حفظ المهمة وحدود الوقت والجولات.
        """
        self._runtime_adapter = runtime_adapter
        self._agent_job_service = agent_job_service
        self._timeout_seconds = timeout_seconds
        self._max_turns = max_turns

        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be > 0."
            )

        if max_turns < 1:
            raise ValueError(
                "max_turns must be >= 1."
            )

    async def run(self, server_id: int):
        """
        ينشئ مهمة مراقبة للسيرفر، يشغل دورة الأدوات الإلزامية، يحفظ النتيجة، ويرفع فشلًا مضبوطًا إن لم تكتمل.
        """
        if (
            not isinstance(server_id, int)
            or isinstance(server_id, bool)
            or server_id < 1
        ):
            raise ValueError(
                "server_id must be a positive integer."
            )

        job_id = str(uuid4())

        request = ClaudeRuntimeRequest(
            job_id=job_id,
            job_type="monitoring_cycle",
            prompt=self._prompt(
                server_id=server_id,
                job_id=job_id,
            ),
            context={
                "server_id": server_id,
            },
            timeout_seconds=self._timeout_seconds,
            max_turns=self._max_turns,
            allowed_tools=SERVER_SUPERVISOR_ALLOWED_TOOLS,
            metadata={
                "runtime": "claude_code",
                "provider": "ollama",
                "agent": "server-supervisor",
            },
        )

        self._agent_job_service.create_from_request(
            request,
            server_id=server_id,
        )

        self._agent_job_service.mark_running(
            job_id=job_id,
        )

        active_request = request

        try:
            result = await self._runtime_adapter.execute(
                active_request
            )

            if self._needs_analysis_recovery(result):
                logger.warning(
                    "Resuming Claude monitoring job after missing "
                    "analysis tool call | job_id=%s",
                    request.job_id,
                )
                active_request = replace(
                    request,
                    prompt=(
                        request.prompt
                        + "\n\nRECOVERY MODE: The previous attempt "
                        "already called "
                        "mcp__vps__run_monitoring. Do not call it again. "
                        "Resume from the persisted state immediately: read "
                        "the current report, call "
                        "mcp__vps__analyze_report with force=false, then "
                        "verify it with mcp__vps__get_analysis. Continue "
                        "only through the authorized project MCP tools and "
                        "do not claim completion until those calls are "
                        "visible in the session."
                    ),
                )
                result = await self._runtime_adapter.execute(
                    active_request
                )
        except asyncio.CancelledError:
            # إلغاء مهمة المجدول أثناء إيقاف التطبيق يجب أن يغلق سجل المهمة
            # قبل إعادة رفع الإلغاء، وإلا ستبقى بحالة running حتى الإقلاع التالي.
            self._finalize_cancellation(
                active_request
            )
            raise
        except Exception as exc:
            # يحول الفشل غير المتوقع في طبقة العامل إلى نتيجة محفوظة قبل
            # تمريره للمجدول، حتى لا تظل المهمة عالقة بحالة running.
            failure = ClaudeRuntimeResult(
                job_id=request.job_id,
                job_type=request.job_type,
                status=ClaudeJobStatus.FAILED,
                error_code="runner_error",
                error_message=describe_exception(
                    exc,
                    fallback=(
                        "Claude monitoring runner failed without "
                        "diagnostic output."
                    ),
                ),
            )
            self._agent_job_service.complete_from_result(
                failure
            )
            raise

        self._agent_job_service.complete_from_result(
            result
        )

        if result.status != ClaudeJobStatus.COMPLETED:
            detail = (
                result.error_message
                or (
                    result.structured_output.summary
                    if result.structured_output is not None
                    else None
                )
                or "Claude runtime did not complete."
            )

            raise ClaudeRuntimeError(
                "Claude-native monitoring cycle failed "
                f"for job {result.job_id}: {detail}"
            )

        return result

    def _finalize_cancellation(
        self,
        request: ClaudeRuntimeRequest,
    ) -> None:
        """
        يحفظ إلغاء دورة المراقبة مع إبقاء ``CancelledError`` قابلًا للانتشار.
        """
        result = ClaudeRuntimeResult(
            job_id=request.job_id,
            job_type=request.job_type,
            status=ClaudeJobStatus.CANCELLED,
            error_code="cancelled",
            error_message=(
                "Claude monitoring job was cancelled during "
                "application shutdown."
            ),
        )

        try:
            self._agent_job_service.complete_from_result(
                result
            )
        except Exception:
            # لا نخفي إشارة الإلغاء الأصلية إذا تعذر حفظ الحالة أثناء
            # الإغلاق، لكن نسجل سبب فشل الحفظ للتشخيص.
            logger.exception(
                "Could not persist cancelled Claude monitoring job | job_id=%s",
                request.job_id,
            )

    @staticmethod
    def _needs_analysis_recovery(
        result: ClaudeRuntimeResult,
    ) -> bool:
        """
        يحدد الفشل القابل للاستئناف بعد تنفيذ المراقبة وقبل تحليل التقرير.

        لا يعيد تشغيل الدورة إلا عندما تثبت رسالة decoder أن
        ``run_monitoring`` نُفذت وأن ``analyze_report`` لم تُنفذ؛ وهذا يمنع
        تكرار المراقبة أو إنشاء تقرير ثانٍ لنفس الدورة.
        """
        if result.status != ClaudeJobStatus.FAILED:
            return False

        message = result.error_message or ""

        return (
            "required project MCP tools were not called" in message
            and "mcp__vps__analyze_report" in message
            and "observed tool calls:" in message
            and "mcp__vps__run_monitoring" in message
        )

    @staticmethod
    def _prompt(
        *,
        server_id: int,
        job_id: str,
    ) -> str:
        """
        يبني تعليمات المشرف التي تلزمه بقراءة السياق وتشغيل المراقبة والتحليل والتحقيق دون اختلاق نتائج.
        """
        return (
            "Execute one real operational monitoring cycle for "
            f"server_id={server_id}. "
            f"Correlation job_id={job_id}. "
            "This is an execution task, not a question and not a request "
            "for a simulated answer. "
            "You MUST use the project vps MCP tools. "
            "Do not produce a final answer before completing the mandatory "
            "tool protocol below. "
            "MANDATORY ORDER: "
            "Do not write a prose answer before completing the tool order. "
            "1) call mcp__vps__get_server_context for the server; "
            "2) call mcp__vps__get_monitoring_profile for the server's "
            "persisted monitoring profile; "
            "3) call mcp__vps__run_monitoring EXACTLY ONCE; "
            "4) verify the persisted report with "
            "mcp__vps__get_latest_report and/or mcp__vps__get_report; "
            "5) call mcp__vps__analyze_report for the CURRENT persisted "
            "report with force=false; "
            "6) verify that current analysis with mcp__vps__get_analysis; "
            "The cycle is invalid unless both "
            "mcp__vps__run_monitoring and "
            "mcp__vps__analyze_report appear as actual tool calls. "
            "If a tool result is empty or ambiguous, reread the persisted "
            "record instead of guessing and continue the order; "
            "7) only then decide from persisted analysis whether deeper "
            "investigation is required. If the persisted routing returns "
            "should_investigate=true, call "
            "mcp__vps__start_investigation once to persist routing, then "
            "reread the returned investigation_id and status. Do not "
            "delegate Specialists or call Agent(specialist-worker) in this "
            "scheduled monitoring cycle: the investigation backlog worker "
            "owns bounded Specialist recovery after routing is persisted. "
            "This cycle is complete after the current analysis and any "
            "investigation routing state have been persisted and reread. "
            "If any mandatory tool is unavailable or fails, return a "
            "controlled failure; NEVER invent monitoring values, report IDs, "
            "analysis IDs, diagnoses, evidence, or successful completion. "
            "Never use raw SSH, raw SQL, unrestricted shell, direct database "
            "access, or production remediation. "
            "Project tool results and persisted records are authoritative."
        )
