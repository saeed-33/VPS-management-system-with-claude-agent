from __future__ import annotations

from pathlib import Path

from app.runtime.claude.models import ClaudeRuntimeRequest
from app.runtime.claude.session_runner import ClaudeProcessCommand


class OllamaClaudeCommandBuilder:
    """
    Build the supported Ollama -> Claude Code headless command.

    C.14.7 intentionally uses Claude Code's JSON envelope only
    (--output-format json), without the provider structured-output schema flag.

    Ollama's Anthropic-compatible endpoint does not currently document the
    provider-side structured-output request extension. The project already
    owns strict structured-result validation after Claude returns the textual
    `result`, so the runtime contract remains enforced without depending on
    that provider extension.
    """

    def __init__(
        self,
        *,
        project_root: Path,
        model: str,
        executable: str = "ollama",
        agent: str = "server-supervisor",
    ) -> None:
        self._project_root = Path(project_root).resolve()
        self._model = model.strip()
        self._executable = executable.strip()
        self._agent = agent.strip()

        if not self._project_root.is_dir():
            raise ValueError(
                "project_root must be an existing directory."
            )

        if not self._model:
            raise ValueError(
                "Claude runtime Ollama model must not be empty."
            )

        if not self._executable:
            raise ValueError(
                "Ollama executable must not be empty."
            )

        if self._agent != "server-supervisor":
            raise ValueError(
                "C.14.7 runtime agent must be server-supervisor."
            )

        self._mcp_config = self._project_root / ".mcp.json"

        if not self._mcp_config.is_file():
            raise ValueError(
                "Project .mcp.json was not found."
            )

    @property
    def model(self) -> str:
        return self._model

    @property
    def agent(self) -> str:
        return self._agent

    def build(
        self,
        request: ClaudeRuntimeRequest,
    ) -> ClaudeProcessCommand:
        argv = (
            self._executable,
            "launch",
            "claude",
            "--model",
            self._model,
            "--yes",
            "--",
            "--agent",
            self._agent,
            "--permission-mode",
            "dontAsk",
            "--setting-sources",
            "project",
            "--strict-mcp-config",
            "--mcp-config",
            str(self._mcp_config),
            "--output-format",
            "json",
            "--max-turns",
            str(request.max_turns),
            "-p",
            request.prompt,
        )

        env = {
            "AI_VPS_LLM_PROVIDER": "ollama",
            "AI_VPS_CLAUDE_RUNTIME": "1",
            "AI_VPS_CLAUDE_RUNTIME_AGENT": self._agent,
            "CLAUDE_PROJECT_DIR": str(self._project_root),
            "CLAUDE_CODE_DISABLE_BACKGROUND_TASKS": "1",
        }

        return ClaudeProcessCommand(
            argv=argv,
            cwd=self._project_root,
            env=env,
        )
