"""
فحص جاهزية بيئة التحقق المعزولة المحلية.

يتحقق وقت التشغيل من المسار والأدوات المطلوبة وحدود البيئة، ويعيد نتيجة منظمة
توضح إن كانت المعالجة التجريبية قابلة للتنفيذ.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from app.core.contracts.sandbox_validation import SandboxRuntimeCheck


class NativeSandboxRuntime:
    """
    يفحص قدرة البيئة المحلية على تشغيل تحقق معزول بالمتطلبات المحددة.
    """

    def check(self) -> SandboxRuntimeCheck:
        """
        يفحص وجود runtime والأدوات والمسارات المطلوبة ويعيد نتيجة جاهزية البيئة المعزولة.
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
