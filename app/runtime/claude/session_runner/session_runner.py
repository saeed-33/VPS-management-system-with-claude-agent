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

from .operations_1 import _SubprocessClaudeSessionRunnerMixin1
from .operations_2 import _SubprocessClaudeSessionRunnerMixin2


class SubprocessClaudeSessionRunner(_SubprocessClaudeSessionRunnerMixin1, _SubprocessClaudeSessionRunnerMixin2):
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
