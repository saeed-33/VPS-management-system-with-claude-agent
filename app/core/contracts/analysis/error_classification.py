"""Contract class extracted from analysis.py during the structure refactor."""

from enum import StrEnum

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

class ErrorClassification(StrEnum):
    """
    تصنيف أولي لطبيعة المشكلة قبل أن يثبت التحقيق سببها.
    """
    NORMAL = "normal"
    DANGEROUS = "dangerous"
    SENSITIVE = "sensitive"
