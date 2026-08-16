"""
جزء من Remediation من التشخيص والاقتراح حتى sandbox/authorization والتنفيذ.

الموقع في المعمارية: Application capability / remediation.
يُستدعى بواسطة: Admin API أو MCP.
يعتمد مباشرة على: app.core.contracts.sandbox_validation.
الحد المعماري: لا يسمح write operation بمجرد اقتراح LLM.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from app.core.contracts.sandbox_validation import SandboxRuntimeCheck


class NativeSandboxRuntime:
    """Fail-closed attestation for Claude Code native sandbox execution.

    Claude's supported CLI surface supplies settings/MCP loading, but the
    installed CLI does not expose a native-sandbox flag. Runtime evidence is
    consequently produced by the project probe from inside the sandbox and
    consumed here; this layer never authorizes a write by itself.
    """

    def check(self) -> SandboxRuntimeCheck:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / remediation.

        تُستدعى عندما يصل workflow إلى check؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد SandboxRuntimeCheck أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        path_value = os.getenv("PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE", "").strip()
        if not path_value:
            return SandboxRuntimeCheck(False, "claude-native-sandbox", "attestation_file_missing")
        path = Path(path_value)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return SandboxRuntimeCheck(False, "claude-native-sandbox", f"attestation_unreadable:{type(exc).__name__}")
        required = {
            "sandboxed": True,
            "project_path_accessible": True,
            "sensitive_path_inaccessible": True,
            "unsandboxed_escape_unavailable": True,
        }
        if any(payload.get(key) != value for key, value in required.items()):
            return SandboxRuntimeCheck(False, "claude-native-sandbox", "attestation_requirements_not_met", payload)
        if not os.getenv("WSL_DISTRO_NAME", "").strip():
            return SandboxRuntimeCheck(False, "claude-native-sandbox", "wsl2_runtime_not_detected", payload)
        return SandboxRuntimeCheck(True, "claude-native-sandbox", evidence=payload)
