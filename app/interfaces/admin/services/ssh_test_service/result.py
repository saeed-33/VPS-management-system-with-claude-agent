"""
اختبار اتصال SSH من واجهة الإدارة.

تحمل الخدمة إعدادات السيرفر ومفتاحه، تنفذ أمرًا بسيطًا للتحقق من الاتصال،
وتعيد نتيجة آمنة قابلة للعرض بدل تسريب استثناءات العميل.
"""
from dataclasses import dataclass

from app.infrastructure.ssh.client.client import SSHClient
from app.infrastructure.ssh.client.config import SSHConnectionConfig
from app.infrastructure.ssh.command_executor.executor import SSHCommandExecutor
from app.infrastructure.database.repositories.server_repository import (
    ServerRepository,
)
from app.core.exceptions.server_not_found_error import ServerNotFoundError


@dataclass(slots=True, frozen=True)
class SSHTestResult:
    """
    يمثل نتيجة اختبار SSH مع الرسالة واسم المضيف عند توفره.
    """
    success: bool
    message: str
    hostname: str | None = None
