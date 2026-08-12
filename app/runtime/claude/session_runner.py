from __future__ import annotations

import asyncio
import json
import os
import signal
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from app.runtime.claude.exceptions import (
    ClaudeProcessExecutionError,
    ClaudeProcessOutputError,
    ClaudeRuntimeError,
)
from app.runtime.claude.models import (
    ClaudeRawResult,
    ClaudeRuntimeRequest,
)


_MAX_ERROR_TEXT = 2000


@dataclass(slots=True, frozen=True)
class ClaudeProcessCommand:
    argv: tuple[str, ...]
    cwd: Path | None = None
    env: dict[str, str] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.argv:
            raise ValueError(
                "Claude process argv must not be empty."
            )

        for item in self.argv:
            if not isinstance(item, str) or not item:
                raise ValueError(
                    "Claude process argv entries must "
                    "be non-empty strings."
                )

        if self.cwd is not None:
            object.__setattr__(
                self,
                "cwd",
                Path(self.cwd).resolve(),
            )


class ClaudeProcessCommandBuilder(Protocol):
    def build(
        self,
        request: ClaudeRuntimeRequest,
    ) -> ClaudeProcessCommand:
        """Build one process command without executing it."""


class ClaudeCliJsonDecoder:
    """
    Decode the documented Claude Code print-mode JSON envelope.

    The runner accepts either:
    - `structured_output`: already validated structured data, or
    - `result`: text returned by Claude Code.

    The existing ClaudeRuntimeAdapter remains responsible for validating
    the project's inner structured result contract.
    """

    def decode(
        self,
        stdout: str,
    ) -> ClaudeRawResult:
        if not stdout.strip():
            raise ClaudeProcessOutputError(
                "Claude process returned empty stdout."
            )

        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise ClaudeProcessOutputError(
                "Claude process stdout was not valid JSON."
            ) from exc

        if not isinstance(payload, dict):
            raise ClaudeProcessOutputError(
                "Claude process JSON output must be an object."
            )

        session_id = payload.get("session_id")
        if (
            not isinstance(session_id, str)
            or not session_id.strip()
        ):
            raise ClaudeProcessOutputError(
                "Claude process JSON output is missing session_id."
            )

        content = self._content(payload)
        turn_count = self._non_negative_int(
            payload,
            "num_turns",
            fallback_key="turn_count",
        )
        tool_call_count = self._non_negative_int(
            payload,
            "tool_call_count",
        )

        usage_metadata = self._usage_metadata(
            payload
        )

        return ClaudeRawResult(
            session_id=session_id.strip(),
            content=content,
            turn_count=turn_count,
            tool_call_count=tool_call_count,
            usage_metadata=usage_metadata,
        )

    @staticmethod
    def _content(
        payload: dict,
    ) -> str:
        structured = payload.get(
            "structured_output"
        )
        if structured is not None:
            if not isinstance(
                structured,
                dict,
            ):
                raise ClaudeProcessOutputError(
                    "structured_output must be an object."
                )

            return json.dumps(
                structured,
                ensure_ascii=False,
                separators=(",", ":"),
            )

        result = payload.get("result")
        if not isinstance(result, str) or not result.strip():
            raise ClaudeProcessOutputError(
                "Claude process JSON output must contain "
                "structured_output or non-empty result."
            )

        return result

    @staticmethod
    def _non_negative_int(
        payload: dict,
        key: str,
        *,
        fallback_key: str | None = None,
    ) -> int:
        value = payload.get(key)

        if (
            value is None
            and fallback_key is not None
        ):
            value = payload.get(
                fallback_key
            )

        if value is None:
            return 0

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            raise ClaudeProcessOutputError(
                f"{key} must be a non-negative integer."
            )

        return value

    @staticmethod
    def _usage_metadata(
        payload: dict,
    ) -> dict:
        usage = payload.get("usage", {})

        if usage is None:
            usage = {}

        if not isinstance(usage, dict):
            raise ClaudeProcessOutputError(
                "usage must be an object when present."
            )

        metadata = dict(usage)

        for key in (
            "total_cost_usd",
            "duration_ms",
            "duration_api_ms",
            "is_error",
            "modelUsage",
        ):
            if key in payload:
                metadata[key] = payload[key]

        return metadata


class SubprocessClaudeSessionRunner:
    """
    Concrete bounded process runner.

    C.14.6 intentionally does not decide which provider/launcher command
    is used. C.14.7 supplies the Ollama-backed command builder.
    """

    def __init__(
        self,
        *,
        command_builder: ClaudeProcessCommandBuilder,
        project_root: Path,
        decoder: ClaudeCliJsonDecoder | None = None,
        base_env: dict[str, str] | None = None,
        terminate_grace_seconds: float = 2.0,
    ) -> None:
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

        if not self._project_root.is_dir():
            raise ValueError(
                "project_root must be an existing directory."
            )

        if self._terminate_grace_seconds <= 0:
            raise ValueError(
                "terminate_grace_seconds must be > 0."
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
        return tuple(
            sorted(self._processes)
        )

    async def run(
        self,
        request: ClaudeRuntimeRequest,
    ) -> ClaudeRawResult:
        command = self._command_builder.build(
            request
        )
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
            stdout_bytes, stderr_bytes = (
                await process.communicate()
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

    async def cancel(
        self,
        identifier: str,
    ) -> None:
        """
        Best-effort cancellation.

        During C.14.6 the active process is indexed by job_id because the
        Claude session_id is only guaranteed in the final JSON envelope.
        C.14.7 may add earlier session-id discovery if stream-json is needed.
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
            # Nothing else is safe to do from the Python host.
            pass

    async def _terminate_windows(
        self,
        process: asyncio.subprocess.Process,
    ) -> None:
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
        diagnostic = (
            stderr.strip()
            or stdout.strip()
            or "no diagnostic output"
        )

        diagnostic = diagnostic[
            :_MAX_ERROR_TEXT
        ]

        return (
            "Claude runtime process exited with "
            f"code {returncode}: {diagnostic}"
        )
