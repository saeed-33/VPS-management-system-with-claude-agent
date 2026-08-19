"""Contract class extracted from analysis.py during the structure refactor."""

from enum import StrEnum

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

class AnalysisHealthStatus(StrEnum):
    """
    التقييم العام لصحة السيرفر كما ظهر من تقرير المراقبة.
    """
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
