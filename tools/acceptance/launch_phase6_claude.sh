#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${WSL_DISTRO_NAME:-}" ]]; then
  echo "PHASE6_SANDBOX_RUNTIME=BLOCKED_BY_SANDBOX_RUNTIME: run from WSL2" >&2
  exit 1
fi

project_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"
attestation_file="${PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE:?Set an attestation output path inside the sandbox}"
export PHASE6_NATIVE_SANDBOX_ATTESTATION_FILE="$attestation_file"

exec claude \
  --settings "$project_dir/.claude/settings.json" \
  --mcp-config "$project_dir/.mcp.json" \
  --strict-mcp-config \
  --add-dir "$project_dir" \
  --permission-mode dontAsk \
  --agent server-supervisor \
  "$@"
