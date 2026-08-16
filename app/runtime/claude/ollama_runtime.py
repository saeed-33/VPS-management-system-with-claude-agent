"""
جزء من Claude Runtime لبناء العملية أو تشغيل الجلسة أو قراءة stream أو تسجيل job.

الموقع في المعمارية: Claude supervisory runtime.
يُستدعى بواسطة: composition أو Scheduler.
يعتمد مباشرة على: app.runtime.claude.models، app.runtime.claude.command.
الحد المعماري: Claude/Ollama للـreasoning/model؛ policy والحفظ والتنفيذ الحتمي في Python.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from pathlib import Path

from app.runtime.claude.models import ClaudeRuntimeRequest
from app.runtime.claude.command import ClaudeProcessCommand


class OllamaClaudeCommandBuilder:
    """
    Run Claude Code directly while using Ollama as its Anthropic-compatible
    backend. This preserves Claude Code's documented JSON envelope and avoids
    depending on the `ollama launch claude` wrapper for MCP/stdout behavior.
    """

    def __init__(
        self,
        *,
        project_root: Path,
        model: str,
        base_url: str,
        executable: str = "claude",
        agent: str = "server-supervisor",
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: project_root، model، base_url، executable، agent.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._project_root = Path(project_root).resolve()
        self._model = model.strip()
        self._base_url = base_url.strip().rstrip("/")
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
        if not self._base_url:
            raise ValueError(
                "Ollama base URL must not be empty."
            )
        if not (
            self._base_url.startswith("http://")
            or self._base_url.startswith("https://")
        ):
            raise ValueError(
                "Ollama base URL must use http:// or https://."
            )
        if not self._executable:
            raise ValueError(
                "Claude executable must not be empty."
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

    def build(
        self,
        request: ClaudeRuntimeRequest,
    ) -> ClaudeProcessCommand:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Claude supervisory runtime.

        تُستدعى عندما يصل workflow إلى build؛ المدخلات المهمة: request.
        تعيد ClaudeProcessCommand أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        argv = (
            self._executable,
            "--model",
            self._model,
            "--agent",
            self._agent,
            "--permission-mode",
            "dontAsk",
            "--allowedTools",
            "mcp__vps__*,Agent(specialist-worker)",
            "--setting-sources",
            "project",
            "--strict-mcp-config",
            "--mcp-config",
            str(self._mcp_config),
            "--output-format",
            "stream-json",
            "--verbose",
            "--max-turns",
            str(request.max_turns),
            "-p",
            request.prompt,
        )

        env = {
            "ANTHROPIC_AUTH_TOKEN": "ollama",
            "ANTHROPIC_API_KEY": "",
            "ANTHROPIC_BASE_URL": self._base_url,
            "ANTHROPIC_DEFAULT_OPUS_MODEL": self._model,
            "ANTHROPIC_DEFAULT_SONNET_MODEL": self._model,
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": self._model,
            "CLAUDE_CODE_SUBAGENT_MODEL": self._model,
            "AI_VPS_LLM_PROVIDER": "ollama",
            "AI_VPS_CLAUDE_RUNTIME": "1",
            "AI_VPS_CLAUDE_RUNTIME_AGENT": self._agent,
            "CLAUDE_PROJECT_DIR": str(self._project_root),
            "CLAUDE_CODE_DISABLE_BACKGROUND_TASKS": "1",
            "MCP_TIMEOUT": "60000",
            "ENABLE_TOOL_SEARCH": "false",
        }

        return ClaudeProcessCommand(
            argv=argv,
            cwd=self._project_root,
            env=env,
        )
