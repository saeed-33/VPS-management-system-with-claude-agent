"""
إدارة عملية Claude على مستوى نظام التشغيل.

تنشئ الخدمة العملية في مجلد آمن، تتابع stdout وstderr بحدود، تمنع الجلسات
المكررة، وتنفذ الإلغاء والتنظيف المناسبين على Windows وPOSIX.
"""
from __future__ import annotations

import asyncio
import os
import signal
import subprocess
from pathlib import Path

from app.runtime.claude.command.process_command import ClaudeProcessCommand
from app.runtime.claude.command.builder import ClaudeProcessCommandBuilder
from app.runtime.claude.exceptions.process_execution_error import ClaudeProcessExecutionError
from app.runtime.claude.exceptions.runtime_error import ClaudeRuntimeError
from app.runtime.claude.exceptions.utils import describe_exception
from app.runtime.claude.models.raw_result import ClaudeRawResult
from app.runtime.claude.models.runtime_request import ClaudeRuntimeRequest


_MAX_ERROR_TEXT = 2000


from app.runtime.claude.stream_decoder.stream_decoder import ClaudeCliJsonDecoder


class _SubprocessClaudeSessionRunnerMixin1:
    """ينظم مجموعة من عمليات المكون."""

    @property
    def active_job_ids(
        self,
    ) -> tuple[str, ...]:
        """
        يعيد معرفات المهام التي ما زالت لها عمليات Claude نشطة.
        """
        return tuple(
            sorted(self._processes)
        )

    async def run(
        self,
        request: ClaudeRuntimeRequest,
    ) -> ClaudeRawResult:
        """
        يبني الأمر، يتحقق من مجلد العمل، يشغل العملية، يقرأ مخرجاتها، ثم يفكها إلى نتيجة خام.
        """
        command = self._command_builder.build(
            request
        )
        # يحول الطلب إلى جلسة تشغيل محدودة؛ لا يقرر ما إذا كان الإجراء مناسبًا
        # للسيرفر ولا يمنح صلاحية تتجاوز قواعد المجال.
        cwd = (
            command.cwd
            if command.cwd is not None
            else self._project_root
        ).resolve()

        self._validate_cwd(
            cwd
        )

        env = dict(self._base_env)
        env.update(command.env)

        process = await self._spawn(
            command=command,
            cwd=cwd,
            env=env,
        )

        async with self._lock:
            if request.job_id in self._processes:
                await self._terminate_process(
                    process
                )
                raise ClaudeRuntimeError(
                    "A Claude process is already active "
                    f"for job {request.job_id}."
                )

            self._processes[
                request.job_id
            ] = process

        try:
            # ننتظر نهاية الجلسة بحدود واضحة حتى لا تتحول جلسة معلقة إلى توقف
            # في مسار المراقبة أو التحقيق.
            stdout_bytes, stderr_bytes = (
                await self._communicate_bounded(
                    process
                )
            )
        except asyncio.CancelledError:
            await self._terminate_process(
                process
            )
            raise
        finally:
            async with self._lock:
                current = self._processes.get(
                    request.job_id
                )
                if current is process:
                    self._processes.pop(
                        request.job_id,
                        None,
                    )

        stdout = stdout_bytes.decode(
            "utf-8",
            errors="replace",
        )
        stderr = stderr_bytes.decode(
            "utf-8",
            errors="replace",
        )

        if process.returncode != 0:
            raise ClaudeProcessExecutionError(
                self._process_error_message(
                    returncode=process.returncode,
                    stderr=stderr,
                    stdout=stdout,
                )
            )

        return self._decoder.decode(
            stdout
        )

    async def _communicate_bounded(
        self,
        process: asyncio.subprocess.Process,
    ) -> tuple[bytes, bytes]:
        """
        يقرأ stdout وstderr بالتوازي وينتظر العملية ضمن حدود تمنع تعليق المهمة.
        """
        stdout_task = asyncio.create_task(
            self._read_stream_bounded(
                process.stdout,
                limit=self._max_stdout_bytes,
                label="stdout",
            )
        )
        stderr_task = asyncio.create_task(
            self._read_stream_bounded(
                process.stderr,
                limit=self._max_stderr_bytes,
                label="stderr",
            )
        )
        wait_task = asyncio.create_task(process.wait())
        tasks = (stdout_task, stderr_task, wait_task)

        try:
            stdout_bytes, stderr_bytes, _ = (
                await asyncio.gather(*tasks)
            )
            return stdout_bytes, stderr_bytes
        except BaseException:
            if process.returncode is None:
                await self._terminate_process(process)
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )
            raise

    @staticmethod
    async def _read_stream_bounded(
        stream: asyncio.StreamReader | None,
        *,
        limit: int,
        label: str,
    ) -> bytes:
        """
        يقرأ قناة العملية حتى نهايتها مع حد أقصى للحجم حتى لا تستهلك جلسة واحدة الذاكرة.
        """
        if stream is None:
            return b""

        chunks: list[bytes] = []
        total = 0

        while True:
            chunk = await stream.read(64 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                raise ClaudeProcessExecutionError(
                    "Claude process "
                    f"{label} exceeded the configured "
                    f"{limit}-byte capture limit."
                )
            chunks.append(chunk)

        return b"".join(chunks)

    async def cancel(
        self,
        identifier: str,
    ) -> None:
        """
        يجد العملية المرتبطة بمعرف المهمة وينهيها إذا كانت لا تزال قيد التشغيل.
        """
        async with self._lock:
            process = self._processes.get(
                identifier
            )

        if process is None:
            return

        await self._terminate_process(
            process
        )

    def _validate_cwd(
        self,
        cwd: Path,
    ) -> None:
        """
        يتأكد أن مجلد الجلسة موجود وداخل مجلد المشروع المسموح قبل تشغيل العملية.
        """
        if cwd != self._project_root:
            raise ClaudeRuntimeError(
                "Claude runtime command must execute from "
                "the configured project_root."
            )
