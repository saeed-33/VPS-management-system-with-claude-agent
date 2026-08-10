from __future__ import annotations

from fastapi import APIRouter

from app.agent.investigation.diagnostic_tools import (
    build_default_diagnostic_tool_registry,
)


router = APIRouter(tags=["diagnostic-tools"])


@router.get("/api/diagnostic-tools")
def list_diagnostic_tools() -> list[dict]:
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
