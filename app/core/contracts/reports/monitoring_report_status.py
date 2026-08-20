"""Contract class extracted from reports.py during the structure refactor."""

from dataclasses import dataclass, field

from datetime import datetime

from enum import StrEnum

class MonitoringReportStatus(StrEnum):
    """
    الحالات التي تصف نتيجة اتصال المراقبة وتنفيذ فحوصها.

    لا يمثل هذا التعداد تشخيص العطل؛ فهو يصف فقط هل اكتملت القياسات أو فشل
    الاتصال أو انتهى التنفيذ بنتيجة جزئية أو فشل عام.
    """
    SUCCESS = "success"
    PARTIAL_FAILURE = "partial_failure"
    CONNECTION_FAILED = "connection_failed"
    FAILED = "failed"
