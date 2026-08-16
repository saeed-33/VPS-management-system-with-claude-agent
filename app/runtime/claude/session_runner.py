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

from app.runtime.claude.command import (
    ClaudeProcessCommand,
    ClaudeProcessCommandBuilder,
)
from app.runtime.claude.exceptions import (
    ClaudeProcessExecutionError,
    ClaudeRuntimeError,
)
from app.runtime.claude.models import ClaudeRawResult, ClaudeRuntimeRequest


_MAX_ERROR_TEXT = 2000


from app.runtime.claude.stream_decoder import ClaudeCliJsonDecoder


class SubprocessClaudeSessionRunner:
    """
    مشغل يتعامل مباشرة مع عملية Claude وتدفق مخرجاتها وإيقافها وتنظيفها.
    """

    def __init__(
        self,
        *,
        command_builder: ClaudeProcessCommandBuilder,
        project_root: Path,
        decoder: ClaudeCliJsonDecoder | None = None,
        base_env: dict[str, str] | None = None,
        terminate_grace_seconds: float = 2.0,
        max_stdout_bytes: int = 16 * 1024 * 1024,
        max_stderr_bytes: int = 2 * 1024 * 1024,
    ) -> None:
        """
        يجهز حدود العملية ومجلد المشروع وسجل العمليات النشطة وأدوات فك المخرجات.
        """
        self._command_builder = (
            command_builder
        )
        self._project_root = Path(
            project_root
        ).resolve()
        self._decoder = (
            decoder
            if decoder is not None
            else ClaudeCliJsonDecoder()
        )
        self._base_env = dict(
            base_env
            if base_env is not None
            else os.environ
        )
        self._terminate_grace_seconds = (
            terminate_grace_seconds
        )
        self._max_stdout_bytes = max_stdout_bytes
        self._max_stderr_bytes = max_stderr_bytes

        if not self._project_root.is_dir():
            raise ValueError(
                "project_root must be an existing directory."
            )

        if self._terminate_grace_seconds <= 0:
            raise ValueError(
                "terminate_grace_seconds must be > 0."
            )

        if self._max_stdout_bytes < 1024:
            raise ValueError(
                "max_stdout_bytes must be >= 1024."
            )

        if self._max_stderr_bytes < 1024:
            raise ValueError(
                "max_stderr_bytes must be >= 1024."
            )

        self._processes: dict[
            str,
            asyncio.subprocess.Process,
        ] = {}
        self._lock = asyncio.Lock()

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

    async def _spawn(
        self,
        *,
        command: ClaudeProcessCommand,
        cwd: Path,
        env: dict[str, str],
    ) -> asyncio.subprocess.Process:
        """
        ينشئ عملية Claude بقنوات مخرجات وبيئة ومجلد عمل مضبوطين.
        """
        kwargs: dict = {}

        if os.name == "nt":
            kwargs["creationflags"] = (
                subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            kwargs["start_new_session"] = True

        try:
            return await (
                asyncio.create_subprocess_exec(
                    *command.argv,
                    cwd=str(cwd),
                    env=env,
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    **kwargs,
                )
            )
        except FileNotFoundError as exc:
            executable = command.argv[0]
            raise ClaudeProcessExecutionError(
                "Claude runtime executable was not found: "
                f"{executable}"
            ) from exc
        except OSError as exc:
            raise ClaudeProcessExecutionError(
                "Claude runtime process could not start."
            ) from exc

    async def _terminate_process(
        self,
        process: asyncio.subprocess.Process,
    ) -> None:
        """
        ينفذ الإيقاف التدريجي ثم القسري للعملية ويضمن ألا تبقى عملية يتيمة.
        """
        if process.returncode is not None:
            return

        if os.name == "nt":
            await self._terminate_windows(
                process
            )
        else:
            self._terminate_posix(
                process
            )

        try:
            await asyncio.wait_for(
                process.wait(),
                timeout=(
                    self._terminate_grace_seconds
                ),
            )
            return
        except TimeoutError:
            pass

        if process.returncode is None:
            process.kill()

        try:
            await asyncio.wait_for(
                process.wait(),
                timeout=(
                    self._terminate_grace_seconds
                ),
            )
        except TimeoutError:
            # بعد فشل الإيقاف القسري لا يحاول المضيف تنفيذ خطوة أخرى قد
            # تزيد أثر العملية أو تترك حالة مضللة عن إيقافها.
            pass

    async def _terminate_windows(
        self,
        process: asyncio.subprocess.Process,
    ) -> None:
        """
        ينهي عملية Claude على Windows وأبناءها بالطريقة المناسبة لنظام التشغيل.
        """
        try:
            killer = await (
                asyncio.create_subprocess_exec(
                    "taskkill",
                    "/PID",
                    str(process.pid),
                    "/T",
                    "/F",
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
            )
            await asyncio.wait_for(
                killer.wait(),
                timeout=(
                    self._terminate_grace_seconds
                ),
            )
        except (
            FileNotFoundError,
            OSError,
            TimeoutError,
        ):
            if process.returncode is None:
                process.terminate()

    @staticmethod
    def _terminate_posix(
        process: asyncio.subprocess.Process,
    ) -> None:
        """
        ينهي مجموعة عملية Claude على POSIX حتى لا تستمر عمليات فرعية بعد الإلغاء.
        """
        try:
            os.killpg(
                process.pid,
                signal.SIGTERM,
            )
        except (
            ProcessLookupError,
            PermissionError,
        ):
            if process.returncode is None:
                process.terminate()

    @staticmethod
    def _process_error_message(
        *,
        returncode: int | None,
        stderr: str,
        stdout: str,
    ) -> str:
        """
        يصوغ رسالة فشل تتضمن حالة العملية ومخرجاتها المفيدة للتشخيص.
        """
        diagnostic = (
            stderr.strip()
            or stdout.strip()
            or "no diagnostic output"
        )

        if len(diagnostic) > _MAX_ERROR_TEXT:
            diagnostic = (
                "...[truncated]..."
                + diagnostic[-(_MAX_ERROR_TEXT - 17):]
            )

        return (
            "Claude runtime process exited with "
            f"code {returncode}: {diagnostic}"
        )
