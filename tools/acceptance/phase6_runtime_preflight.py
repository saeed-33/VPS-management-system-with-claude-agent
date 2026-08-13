from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


REQUIRED_SUPPORTED_FLAGS = ("--settings", "--mcp-config", "--strict-mcp-config", "--add-dir")


def main() -> int:
    executable = os.getenv("CLAUDE_RUNTIME_EXECUTABLE", "claude")
    path = shutil.which(executable)
    if path is None:
        print("PHASE6_SANDBOX_RUNTIME=BLOCKED_BY_SANDBOX_RUNTIME: Claude executable unavailable")
        return 1
    result = subprocess.run([path, "--help"], capture_output=True, text=True, check=False)
    missing = [flag for flag in REQUIRED_SUPPORTED_FLAGS if flag not in result.stdout]
    if missing:
        print("PHASE6_SANDBOX_RUNTIME=BLOCKED_BY_SANDBOX_RUNTIME: unsupported CLI flags: " + ", ".join(missing))
        return 1
    print("PHASE6_SANDBOX_RUNTIME=SUPPORTED_CLI_SURFACE")
    print("Use --settings .claude/settings.json --mcp-config .mcp.json --strict-mcp-config --add-dir <project>.")
    print("Native sandbox acceptance still requires an attestation produced from inside the sandbox.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
