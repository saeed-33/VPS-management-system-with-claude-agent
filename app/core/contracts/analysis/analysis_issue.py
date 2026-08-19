"""Contract class extracted from analysis.py during the structure refactor."""

from enum import StrEnum

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from .analysis_severity import AnalysisSeverity

from .error_classification import ErrorClassification

class AnalysisIssue(BaseModel):
    """
    مشكلة مستخرجة من تقرير المراقبة مع شدتها ووصفها وقرينتها الأولية.

    قد تحمل توصية مبدئية، لكنها لا تتحول إلى معالجة معتمدة قبل أن يراجعها
    التحقيق والأدلة الحالية.
    """
    severity: AnalysisSeverity
    classification: ErrorClassification | None = None

    title: str = Field(
        min_length=1,
        max_length=250,
    )

    description: str = Field(
        min_length=1,
    )

    evidence: str | None = None
    recommendation: str | None = None

    model_config = ConfigDict(
        extra="forbid",
    )
