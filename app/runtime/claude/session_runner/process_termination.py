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


class _ProcessTerminationMixin:
    """ينظم مجموعة من عمليات المكون."""

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
                "Claude runtime process could not start: "
                + describe_exception(
                    exc,
                    fallback="operating-system error without details.",
                )
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
