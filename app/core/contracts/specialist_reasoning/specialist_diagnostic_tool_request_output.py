"""Contract class extracted from specialist_reasoning.py during the structure refactor."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

class SpecialistDiagnosticToolRequestOutput(BaseModel):
    """
    طلب فحص إضافي يشرح المتخصص سبب حاجته إليه.

    لا يمثل الطلب إذنًا بالتنفيذ؛ تمر الأداة لاحقًا عبر سياسة التحقيق والتحقق
    من المعاملات قبل جمع دليل جديد.
    """
    model_config = ConfigDict(extra="forbid")

    tool_id: str = Field(min_length=1, max_length=120)
    arguments: dict[str, Any] = Field(default_factory=dict)
    rationale: str = Field(min_length=1, max_length=1000)
