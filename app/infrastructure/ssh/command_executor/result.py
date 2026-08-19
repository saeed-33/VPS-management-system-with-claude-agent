"""
تنفيذ فحص مراقبة واحد عبر اتصال SSH وإرجاع نتيجته المقاسة.
"""
import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter

import asyncssh

from app.infrastructure.ssh.client.client import SSHClient


@dataclass(slots=True)


class CommandExecutionResult:
    """
    نتيجة فحص SSH مع المخرج والحالة والمدة والبصمة اللازمة للتقرير.
    """
    command_id: int | None
    command_name: str
    command_text: str
    execution_order: int

    success: bool
    exit_status: int | None

    stdout: str
    stderr: str
    error_message: str | None

    fingerprint_strategy: str
    fingerprint_config: dict

    started_at: datetime
    finished_at: datetime
    duration_ms: float
