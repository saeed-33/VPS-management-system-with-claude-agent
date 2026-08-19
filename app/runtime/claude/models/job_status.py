"""
نماذج البيانات التي تصف طلب جلسة Claude ونتيجتها وحالتها.

تمنع هذه النماذج انتقال طلب ناقص أو نتيجة غير قابلة للتفسير إلى بقية رحلة
المراقبة، وتفصل بين المخرجات الخام والنتيجة المنظمة والحالة المحفوظة.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ClaudeJobStatus(StrEnum):
    """
    الحالات المسموح بها لدورة مهمة Claude منذ الانتظار حتى النهاية.
    """
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"

