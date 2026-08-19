"""Contract class extracted from investigation.py during the structure refactor."""

from __future__ import annotations

from dataclasses import dataclass, field

from enum import StrEnum

from typing import Any

class EvidenceKind(StrEnum):
    """
    مصادر الدليل التي يمكن أن يستند إليها التحقيق.

    يوضح النوع هل الدليل تقرير مراقبة، نتيجة أمر، تحليل، حادثة تاريخية، وثيقة
    معرفة، أم نتيجة مشتقة من أدلة أخرى.
    """
    MONITORING_REPORT = "monitoring_report"
    COMMAND_RESULT = "command_result"
    ANALYSIS = "analysis"
    HISTORICAL_INCIDENT = "historical_incident"
    KNOWLEDGE_DOCUMENT = "knowledge_document"
    DERIVED_FINDING = "derived_finding"
