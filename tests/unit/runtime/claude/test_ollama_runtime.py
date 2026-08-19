"""Tests for test ollama runtime.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: app.runtime.claude.models، app.runtime.claude.ollama_runtime.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from pathlib import Path

from app.runtime.claude.models.runtime_request import ClaudeRuntimeRequest
from app.runtime.claude.ollama_runtime import (
    OllamaClaudeCommandBuilder,
)


def test_direct_claude_uses_ollama_backend(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_direct_claude_uses_ollama_backend؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    project = tmp_path / "project"
    project.mkdir()
    (project / ".mcp.json").write_text(
        '{"mcpServers":{}}',
        encoding="utf-8",
    )

    builder = OllamaClaudeCommandBuilder(
        project_root=project,
        model="gemma-test",
        base_url="http://127.0.0.1:11434",
        executable="claude",
    )

    request = ClaudeRuntimeRequest(
        job_id="job-1",
        job_type="monitoring_cycle",
        prompt="monitor server 7",
        max_turns=13,
    )

    command = builder.build(request)
    argv = command.argv
    env = command.env

    assert argv[0] == "claude"
    assert "launch" not in argv
    assert argv[argv.index("--model") + 1] == "gemma-test"
    assert argv[argv.index("--agent") + 1] == "server-supervisor"
    assert argv[argv.index("--allowedTools") + 1] == (
        "mcp__vps__*,Agent(specialist-worker)"
    )
    assert "Bash" not in argv[argv.index("--allowedTools") + 1]
    assert argv[argv.index("--output-format") + 1] == "stream-json"
    assert "--verbose" in argv
    assert argv[argv.index("--setting-sources") + 1] == "project"
    assert "--strict-mcp-config" in argv
    assert "--json-schema" not in argv
    assert argv[-2] == "-p"
    assert argv[-1] == "monitor server 7"

    assert env["ANTHROPIC_AUTH_TOKEN"] == "ollama"
    assert env["ANTHROPIC_API_KEY"] == ""
    assert env["ANTHROPIC_BASE_URL"] == "http://127.0.0.1:11434"
    assert env["CLAUDE_CODE_SUBAGENT_MODEL"] == "gemma-test"
    assert env["AI_VPS_LLM_PROVIDER"] == "ollama"


def test_runtime_composition_uses_direct_claude_settings():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_composition_uses_direct_claude_settings؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    root = Path(__file__).resolve().parents[1]
    text = (
        root
        / "app"
        / "composition"
        / "runtime.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "base_url=settings.ollama_base_url" in text
    assert "settings.claude_runtime_executable" in text
