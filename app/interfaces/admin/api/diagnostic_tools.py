"""
Endpoint من Admin API يحول HTTP إلى application service ويعيد schema للمشغل.

الموقع في المعمارية: HTTP interface / adapter.
يُستدعى بواسطة: عميل الإدارة عبر FastAPI.
يعتمد مباشرة على: app.core.policies.diagnostic_tools.
الحد المعماري: لا يضع business rules أو transaction logic.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.core.policies.diagnostic_tools import (
    build_default_diagnostic_tool_registry,
)


router = APIRouter(tags=["diagnostic-tools"])


@router.get("/api/diagnostic-tools")
def list_diagnostic_tools() -> list[dict]:
    """
    يقرأ أو يسترجع البيانات مع الحفاظ على semantics الكيان ضمن طبقة HTTP interface / adapter.

    تُستدعى عندما يصل workflow إلى list_diagnostic_tools؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد list[dict] أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    registry = build_default_diagnostic_tool_registry()

    return [
        {
            "tool_id": item.tool_id,
            "name": item.name,
            "description": item.description,
            "domains": list(item.domains),
            "timeout_seconds": item.timeout_seconds,
            "requires_sudo": item.requires_sudo,
            "risk": item.risk.value,
            "output_limit_chars": item.output_limit_chars,
            "parameters": [
                {
                    "name": parameter.name,
                    "kind": parameter.kind.value,
                    "required": parameter.required,
                    "default": parameter.default,
                    "minimum": parameter.minimum,
                    "maximum": parameter.maximum,
                    "description": parameter.description,
                }
                for parameter in item.parameters
            ],
        }
        for item in registry.definitions
    ]
