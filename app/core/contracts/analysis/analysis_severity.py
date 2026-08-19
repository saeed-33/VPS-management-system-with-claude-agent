"""Contract class extracted from analysis.py during the structure refactor."""

from enum import StrEnum

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

class AnalysisSeverity(StrEnum):
    """
    شدة ملاحظة أو مشكلة اكتشفها تحليل التقرير.
    """
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
