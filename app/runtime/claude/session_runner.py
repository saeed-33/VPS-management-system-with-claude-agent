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
    Decode Claude Code output for C.14.7.

    The operational runtime uses stream-json. For compatibility, this decoder
    also accepts the single-object JSON envelope and the batched event-array
    shape observed from Claude Code 2.1.175.

    VPS operational sessions are fail-closed: success requires a connected
    `vps` MCP server plus authoritative calls to run_monitoring and
    analyze_report. The returned structured envelope is synthesized from
    runtime evidence, not from free-form model claims.
    """

    _REQUIRED_VPS_TOOLS = frozenset(
        {
            "mcp__vps__run_monitoring",
            "mcp__vps__analyze_report",
        }
    )

    def decode(
        self,
        stdout: str,
    ) -> ClaudeRawResult:
        events = self._parse_stdout(
            stdout
        )

        if isinstance(events, dict):
            return self._decode_single_envelope(
                events
            )

        return self._decode_event_sequence(
            events
        )

    def _parse_stdout(
        self,
        stdout: str,
    ) -> dict | list[dict]:
        stripped = stdout.strip()

        if not stripped:
            raise ClaudeProcessOutputError(
                "Claude process returned empty stdout."
            )

        # First accept a normal JSON object or the batched array observed in
        # Claude Code 2.1.175.
        try:
            payload = json.loads(
                stripped
            )
        except json.JSONDecodeError:
            payload = None

        if isinstance(payload, dict):
            return payload

        if isinstance(payload, list):
            if not all(
                isinstance(item, dict)
                for item in payload
            ):
                raise ClaudeProcessOutputError(
                    "Claude JSON event array must contain only objects."
                )
            return payload

        # Official stream-json is newline-delimited JSON.
        events: list[dict] = []

        for line_number, line in enumerate(
            stdout.splitlines(),
            start=1,
        ):
            candidate = line.strip()

            if not candidate:
                continue

            try:
                event = json.loads(
                    candidate
                )
            except json.JSONDecodeError as exc:
                raise ClaudeProcessOutputError(
                    "Claude stream-json contained invalid JSON "
                    f"on line {line_number}."
                ) from exc

            if not isinstance(event, dict):
                raise ClaudeProcessOutputError(
                    "Claude stream-json lines must be JSON objects."
                )

            events.append(event)

        if not events:
            raise ClaudeProcessOutputError(
                "Claude stream-json contained no events."
            )

        return events

    def _decode_single_envelope(
        self,
        payload: dict,
    ) -> ClaudeRawResult:
        session_id = self._session_id(
            payload
        )

        self._raise_for_result_error(
            payload
        )

        content = self._content_from_envelope(
            payload
        )

        return ClaudeRawResult(
            session_id=session_id,
            content=content,
            turn_count=self._non_negative_int(
                payload,
                "num_turns",
                fallback_key="turn_count",
            ),
            tool_call_count=self._non_negative_int(
                payload,
                "tool_call_count",
            ),
            usage_metadata=self._usage_metadata(
                payload
            ),
        )

    def _decode_event_sequence(
        self,
        events: list[dict],
    ) -> ClaudeRawResult:
        init_events = [
            event
            for event in events
            if (
                event.get("type") == "system"
                and event.get("subtype") == "init"
            )
        ]

        if len(init_events) != 1:
            raise ClaudeProcessOutputError(
                "Claude event stream must contain exactly "
                "one system/init event."
            )

        result_events = [
            event
            for event in events
            if event.get("type") == "result"
        ]

        if len(result_events) != 1:
            raise ClaudeProcessOutputError(
                "Claude event stream must contain exactly "
                "one result event."
            )

        init_event = init_events[0]
        result_event = result_events[0]

        init_session_id = self._session_id(
            init_event
        )
        result_session_id = self._session_id(
            result_event
        )

        if init_session_id != result_session_id:
            raise ClaudeProcessOutputError(
                "Claude event stream session_id mismatch."
            )

        self._raise_for_result_error(
            result_event
        )

        tool_names = self._event_tool_names(
            events
        )

        mcp_servers = self._mcp_servers(
            init_event
        )

        vps_server = next(
            (
                item
                for item in mcp_servers
                if item.get("name") == "vps"
            ),
            None,
        )

        if vps_server is not None:
            content = self._operational_vps_content(
                session_id=result_session_id,
                vps_server=vps_server,
                tool_names=tool_names,
            )
        else:
            content = self._event_content(
                result_event=result_event,
                events=events,
            )

        usage_metadata = self._usage_metadata(
            result_event
        )

        if tool_names:
            usage_metadata[
                "event_tool_names"
            ] = tool_names

        if mcp_servers:
            usage_metadata[
                "event_mcp_servers"
            ] = mcp_servers

        return ClaudeRawResult(
            session_id=result_session_id,
            content=content,
            turn_count=self._non_negative_int(
                result_event,
                "num_turns",
                fallback_key="turn_count",
            ),
            tool_call_count=max(
                self._non_negative_int(
                    result_event,
                    "tool_call_count",
                ),
                len(tool_names),
            ),
            usage_metadata=usage_metadata,
        )

    def _operational_vps_content(
        self,
        *,
        session_id: str,
        vps_server: dict,
        tool_names: list[str],
    ) -> str:
        status = vps_server.get(
            "status"
        )

        if status != "connected":
            raise ClaudeProcessOutputError(
                "Claude operational session cannot be accepted: "
                f"vps MCP status={status!r}."
            )

        used = set(
            tool_names
        )
        missing = sorted(
            self._REQUIRED_VPS_TOOLS
            - used
        )

        if missing:
            raise ClaudeProcessOutputError(
                "Claude operational session cannot be accepted: "
                "required project MCP tools were not called: "
                + ", ".join(missing)
            )

        # This is deliberately not a diagnosis. Authoritative report,
        # analysis, investigation, and evidence live in project persistence.
        # The envelope only certifies that the bounded operational workflow
        # actually executed through the project MCP boundary.
        envelope = {
            "status": "completed",
            "summary": (
                "Claude operational monitoring cycle completed "
                "through the project MCP boundary."
            ),
            "data": {
                "session_id": session_id,
                "required_tools_verified": sorted(
                    self._REQUIRED_VPS_TOOLS
                ),
                "tool_calls": list(
                    tool_names
                ),
            },
            "metadata": {
                "result_source": (
                    "runtime_mcp_evidence"
                ),
                "mcp_server": "vps",
                "mcp_status": status,
            },
        }

        return json.dumps(
            envelope,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def _event_content(
        self,
        *,
        result_event: dict,
        events: list[dict],
    ) -> str:
        try:
            return self._content_from_envelope(
                result_event
            )
        except ClaudeProcessOutputError as exc:
            text = self._final_assistant_text(
                events
            )

            if text is None:
                raise ClaudeProcessOutputError(
                    "Claude successful event stream contained "
                    "no safe final assistant text."
                ) from exc

            return text

    @staticmethod
    def _final_assistant_text(
        events: list[dict],
    ) -> str | None:
        for event in reversed(
            events
        ):
            if event.get("type") != "assistant":
                continue

            message = event.get(
                "message"
            )

            if not isinstance(
                message,
                dict,
            ):
                continue

            content = message.get(
                "content"
            )

            if not isinstance(
                content,
                list,
            ):
                continue

            # Do not mistake an intermediate tool-use turn for the final
            # assistant response.
            if any(
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                for block in content
            ):
                continue

            text_parts = [
                block.get(
                    "text",
                    "",
                )
                for block in content
                if (
                    isinstance(
                        block,
                        dict,
                    )
                    and block.get(
                        "type"
                    )
                    == "text"
                    and isinstance(
                        block.get(
                            "text"
                        ),
                        str,
                    )
                    and block.get(
                        "text"
                    ).strip()
                )
            ]

            text = "".join(
                text_parts
            ).strip()

            if text:
                return text

        return None

    @staticmethod
    def _event_tool_names(
        events: list[dict],
    ) -> list[str]:
        names: list[str] = []

        for event in events:
            if event.get("type") != "assistant":
                continue

            message = event.get(
                "message"
            )

            if not isinstance(
                message,
                dict,
            ):
                continue

            content = message.get(
                "content"
            )

            if not isinstance(
                content,
                list,
            ):
                continue

            for block in content:
                if not isinstance(
                    block,
                    dict,
                ):
                    continue

                if (
                    block.get("type")
                    != "tool_use"
                ):
                    continue

                name = block.get(
                    "name"
                )

                if (
                    isinstance(
                        name,
                        str,
                    )
                    and name.strip()
                ):
                    names.append(
                        name.strip()
                    )

        return names

    @staticmethod
    def _mcp_servers(
        init_event: dict,
    ) -> list[dict]:
        value = init_event.get(
            "mcp_servers",
            [],
        )

        if not isinstance(
            value,
            list,
        ):
            return []

        return [
            dict(item)
            for item in value
            if isinstance(
                item,
                dict,
            )
        ]

    @staticmethod
    def _session_id(
        payload: dict,
    ) -> str:
        value = payload.get(
            "session_id"
        )

        if (
            not isinstance(
                value,
                str,
            )
            or not value.strip()
        ):
            raise ClaudeProcessOutputError(
                "Claude output is missing session_id."
            )

        return value.strip()

    @staticmethod
    def _raise_for_result_error(
        payload: dict,
    ) -> None:
        if payload.get(
            "type"
        ) != "result":
            return

        subtype = payload.get(
            "subtype"
        )
        is_error = payload.get(
            "is_error"
        )

        if (
            isinstance(
                subtype,
                str,
            )
            and subtype
            and subtype != "success"
        ):
            raise ClaudeProcessOutputError(
                "Claude result reported failure: "
                f"subtype={subtype}; "
                f"num_turns={payload.get('num_turns')}; "
                f"stop_reason={payload.get('stop_reason')}; "
                f"is_error={is_error}; "
                f"session_id={payload.get('session_id')}"
            )

        if is_error is True:
            raise ClaudeProcessOutputError(
                "Claude result reported is_error=true "
                f"with subtype={subtype!r}."
            )

    @staticmethod
    def _content_from_envelope(
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

        result = payload.get(
            "result"
        )

        if (
            not isinstance(
                result,
                str,
            )
            or not result.strip()
        ):
            raise ClaudeProcessOutputError(
                "Claude successful output does not contain "
                "structured_output or a non-empty result."
            )

        return result

    @staticmethod
    def _non_negative_int(
        payload: dict,
        key: str,
        *,
        fallback_key: str | None = None,
    ) -> int:
        value = payload.get(
            key
        )

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
            not isinstance(
                value,
                int,
            )
            or isinstance(
                value,
                bool,
            )
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
        usage = payload.get(
            "usage",
            {},
        )

        if usage is None:
            usage = {}

        if not isinstance(
            usage,
            dict,
        ):
            raise ClaudeProcessOutputError(
                "usage must be an object when present."
            )

        metadata = dict(
            usage
        )

        for key in (
            "total_cost_usd",
            "duration_ms",
            "duration_api_ms",
            "is_error",
            "modelUsage",
            "subtype",
            "stop_reason",
        ):
            if key in payload:
                metadata[
                    key
                ] = payload[
                    key
                ]

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
        max_stdout_bytes: int = 16 * 1024 * 1024,
        max_stderr_bytes: int = 2 * 1024 * 1024,
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
