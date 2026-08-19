"""Contract class extracted from final_diagnosis.py during the structure refactor."""

from __future__ import annotations

from abc import ABC, abstractmethod

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

@dataclass(slots=True, frozen=True)
class FinalDiagnosisNarrative:
    """
    صياغة تشخيص نهائي محفوظة مع مصدر النموذج وبيان استخدام fallback.
    """
    summary: str
    claim_ids: tuple[str, ...]
    conflict_ids: tuple[str, ...]
    operator_notes: tuple[str, ...]
    provider_name: str
    model_name: str
    used_fallback: bool
    metadata: dict
