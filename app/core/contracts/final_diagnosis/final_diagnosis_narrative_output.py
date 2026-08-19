"""Contract class extracted from final_diagnosis.py during the structure refactor."""

from __future__ import annotations

from abc import ABC, abstractmethod

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

class FinalDiagnosisNarrativeOutput(BaseModel):
    """
    النص المنظم الذي يعيده مزود صياغة التشخيص النهائي.

    يقتصر على ملخص ومعرفات الادعاءات والتعارضات وملاحظات المشغل، ولا يسمح
    بإضافة دليل أو إجراء غير موجود في حالة التحقيق.
    """
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=2000)
    claim_ids: list[str] = Field(default_factory=list)
    conflict_ids: list[str] = Field(default_factory=list)
    operator_notes: list[str] = Field(default_factory=list, max_length=5)
