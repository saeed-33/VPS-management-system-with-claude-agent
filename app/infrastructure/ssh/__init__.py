"""
اتصال SSH وتنفيذ فحوص القراءة على السيرفرات البعيدة.
"""

from asyncssh import Error as SSHError

from app.infrastructure.ssh.client import SSHClient, SSHConnectionConfig
from app.infrastructure.ssh.command_executor import (
    CommandExecutionResult,
    SSHCommandExecutor,
)

__all__ = [
    "SSHClient",
    "SSHConnectionConfig",
    "SSHCommandExecutor",
    "CommandExecutionResult",
    "SSHError",
]
