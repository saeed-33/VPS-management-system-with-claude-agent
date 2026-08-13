from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> int:
    project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", Path.cwd())).resolve()
    cwd = Path.cwd().resolve()
    sandbox_marker = os.getenv("PHASE6_NATIVE_SANDBOX", "").strip().lower() == "true"
    sensitive_paths = [item for item in os.getenv("PHASE6_SENSITIVE_PATHS", "").split(os.pathsep) if item]
    sensitive_inaccessible = all(not Path(item).exists() for item in sensitive_paths)
    payload = {
        "sandboxed": sandbox_marker,
        "project_path_accessible": cwd == project_root or project_root in cwd.parents,
        "sensitive_path_inaccessible": sensitive_inaccessible,
        "unsandboxed_escape_unavailable": os.getenv("PHASE6_UNSANDBOXED_ESCAPE_DENIED", "").strip().lower() == "true",
        "cwd": str(cwd),
        "project_root": str(project_root),
        "runtime": "claude-native-sandbox",
    }
    output = os.getenv("PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE", "").strip()
    if output:
        Path(output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if all(payload[key] for key in (
        "sandboxed", "project_path_accessible", "sensitive_path_inaccessible", "unsandboxed_escape_unavailable"
    )) else 1


if __name__ == "__main__":
    raise SystemExit(main())
