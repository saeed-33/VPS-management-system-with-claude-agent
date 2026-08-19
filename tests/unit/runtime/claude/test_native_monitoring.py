"""Tests for test native monitoring.
اختبارات دورة المراقبة الأصلية التي تضمن إغلاق سجل المهمة عند الإلغاء أو الفشل.
"""
from __future__ import annotations

import asyncio

import pytest

from app.runtime.claude.exceptions.runtime_error import ClaudeRuntimeError
from app.runtime.claude.models.job_status import ClaudeJobStatus
from app.runtime.claude.models.runtime_result import ClaudeRuntimeResult
from app.runtime.claude.native_monitoring import (
    ClaudeNativeMonitoringRunner,
)


class RecordingJobService:
    """خدمة اختبار تحفظ انتقالات المهمة في الذاكرة."""

    def __init__(self) -> None:
        self.created = []
        self.running = []
        self.completed = []

    def create_from_request(self, request, *, server_id=None):
        self.created.append((request, server_id))

    def mark_running(self, *, job_id, session_id=None):
        self.running.append((job_id, session_id))

    def complete_from_result(self, result):
        self.completed.append(result)


class BlockingRuntimeAdapter:
    """محول يبقى معلقًا حتى يلغيه الاختبار."""

    def __init__(self) -> None:
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def execute(self, request):
        self.started.set()
        await self.release.wait()


class RaisingRuntimeAdapter:
    """محول يرفع خطأً من طبقة التشغيل لاختبار إغلاق السجل."""

    async def execute(self, request):
        raise ValueError()


class RecoveryRuntimeAdapter:
    """محول يعيد فشل نقص التحليل ثم نجاح الاستئناف."""

    def __init__(self) -> None:
        self.requests = []

    async def execute(self, request):
        self.requests.append(request)

        if len(self.requests) == 1:
            return ClaudeRuntimeResult(
                job_id=request.job_id,
                job_type=request.job_type,
                status=ClaudeJobStatus.FAILED,
                error_code="runtime_error",
                error_message=(
                    "Claude operational session cannot be accepted: "
                    "required project MCP tools were not called: "
                    "mcp__vps__analyze_report; observed tool calls: "
                    "mcp__vps__run_monitoring"
                ),
            )

        return ClaudeRuntimeResult(
            job_id=request.job_id,
            job_type=request.job_type,
            status=ClaudeJobStatus.COMPLETED,
        )


def make_runner(adapter, service):
    return ClaudeNativeMonitoringRunner(
        runtime_adapter=adapter,
        agent_job_service=service,
        timeout_seconds=30.0,
        max_turns=4,
    )


def test_shutdown_cancellation_persists_terminal_cancelled_job():
    """
    يثبت أن إلغاء مهمة المراقبة لا يتركها بحالة running.
    """
    async def scenario():
        service = RecordingJobService()
        adapter = BlockingRuntimeAdapter()
        runner = make_runner(adapter, service)

        task = asyncio.create_task(runner.run(server_id=3))
        await adapter.started.wait()

        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert len(service.completed) == 1
        result = service.completed[0]
        assert result.status == ClaudeJobStatus.CANCELLED
        assert result.error_code == "cancelled"
        assert "shutdown" in result.error_message

    asyncio.run(scenario())


def test_unexpected_runner_failure_is_persisted_before_propagation():
    """
    يثبت أن فشل العامل غير المتوقع يغلق سجل المهمة برسالة تشخيصية.
    """
    async def scenario():
        service = RecordingJobService()
        runner = make_runner(
            RaisingRuntimeAdapter(),
            service,
        )

        with pytest.raises(ValueError):
            await runner.run(server_id=3)

        assert len(service.completed) == 1
        result = service.completed[0]
        assert result.status == ClaudeJobStatus.FAILED
        assert result.error_code == "runner_error"
        assert result.error_message
        assert "ValueError" in result.error_message

    asyncio.run(scenario())


def test_missing_analysis_resumes_without_rerunning_monitoring():
    """
    يثبت أن استئناف الفشل لا يعيد استدعاء run_monitoring.
    """
    async def scenario():
        service = RecordingJobService()
        adapter = RecoveryRuntimeAdapter()
        runner = make_runner(adapter, service)

        result = await runner.run(server_id=3)

        assert result.status == ClaudeJobStatus.COMPLETED
        assert len(adapter.requests) == 2
        assert "RECOVERY MODE" in adapter.requests[1].prompt
        assert "Do not call it again" in adapter.requests[1].prompt
        assert len(service.completed) == 1
        assert service.completed[0].status == ClaudeJobStatus.COMPLETED

    asyncio.run(scenario())
