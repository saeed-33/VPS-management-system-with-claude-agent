"""Tests for test runtime hooks.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HOOK = ROOT / "tools" / "claude_hooks" / "runtime_hooks.py"


def read_settings() -> dict:
    """
    يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى read_settings؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد dict أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return json.loads(
        (ROOT / ".claude/settings.json").read_text(
            encoding="utf-8"
        )
    )


def run_hook(
    payload: dict,
    tmp_path: Path,
    *,
    provider: str = "ollama",
):
    """
    ينفذ مرحلة الأداة أو يحفظ نتيجة التقييم ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى run_hook؛ المدخلات المهمة: payload، tmp_path، provider.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(ROOT)
    env["AI_VPS_LLM_PROVIDER"] = provider
    env["AI_VPS_RUNTIME_HOOK_AUDIT_DIR"] = str(
        tmp_path / "events"
    )

    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )

    output = (
        json.loads(result.stdout)
        if result.stdout.strip()
        else None
    )
    return result, output, Path(
        env["AI_VPS_RUNTIME_HOOK_AUDIT_DIR"]
    )


def runtime_payload(event: str) -> dict:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى runtime_payload؛ المدخلات المهمة: event.
    تعيد dict أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return {
        "session_id": "session-test",
        "cwd": str(ROOT),
        "permission_mode": "dontAsk",
        "hook_event_name": event,
        "agent_type": "server-supervisor",
    }


def test_settings_register_only_concrete_runtime_hooks():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_settings_register_only_concrete_runtime_hooks؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    hooks = read_settings()["hooks"]

    assert set(hooks) == {
        "SessionStart",
        "UserPromptSubmit",
        "ConfigChange",
        "SubagentStart",
        "SubagentStop",
        "SessionEnd",
    }

    assert hooks["SessionStart"][0]["matcher"] == (
        "startup|resume"
    )
    assert hooks["ConfigChange"][0]["matcher"] == (
        "project_settings|local_settings|skills"
    )
    assert hooks["SubagentStart"][0]["matcher"] == (
        "specialist-worker"
    )
    assert hooks["SubagentStop"][0]["matcher"] == (
        "specialist-worker"
    )


def test_hook_handlers_use_cross_platform_exec_form():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_hook_handlers_use_cross_platform_exec_form؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    hooks = read_settings()["hooks"]

    handlers = []
    for groups in hooks.values():
        for group in groups:
            handlers.extend(group["hooks"])

    for handler in handlers:
        assert handler["type"] == "command"
        assert handler["command"] == "python"
        assert handler["args"] == [
            (
                "${CLAUDE_PROJECT_DIR}/tools/"
                "claude_hooks/runtime_hooks.py"
            )
        ]
        assert handler["timeout"] == 5


def test_normal_development_session_is_ignored(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_normal_development_session_is_ignored؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    payload = {
        "session_id": "dev-session",
        "cwd": str(ROOT),
        "permission_mode": "default",
        "hook_event_name": "UserPromptSubmit",
        "prompt": "development prompt",
    }

    result, output, audit_dir = run_hook(
        payload,
        tmp_path,
        provider="anthropic",
    )

    assert result.returncode == 0
    assert output is None
    assert not audit_dir.exists()


def test_runtime_preflight_passes_current_c14_contract(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_preflight_passes_current_c14_contract؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    payload = runtime_payload("UserPromptSubmit")
    payload["prompt"] = "run server 1"

    result, output, audit_dir = run_hook(
        payload,
        tmp_path,
    )

    assert result.returncode == 0
    assert "decision" not in output
    assert "preflight passed" in (
        output["hookSpecificOutput"]["additionalContext"]
    )

    files = list(audit_dir.rglob("*.json"))
    assert files


def test_runtime_preflight_blocks_non_ollama_provider(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_preflight_blocks_non_ollama_provider؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    payload = runtime_payload("UserPromptSubmit")

    result, output, _ = run_hook(
        payload,
        tmp_path,
        provider="anthropic",
    )

    assert result.returncode == 0
    assert output["decision"] == "block"
    assert "AI_VPS_LLM_PROVIDER" in output["reason"]


def test_session_start_adds_runtime_context_without_blocking(
    tmp_path,
):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_session_start_adds_runtime_context_without_blocking؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    payload = runtime_payload("SessionStart")
    payload["source"] = "startup"
    payload["model"] = "runtime-model"

    result, output, _ = run_hook(payload, tmp_path)

    assert result.returncode == 0
    assert "decision" not in output
    assert (
        output["hookSpecificOutput"]["hookEventName"]
        == "SessionStart"
    )


def test_runtime_config_change_is_blocked(tmp_path):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_config_change_is_blocked؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    payload = runtime_payload("ConfigChange")
    payload["source"] = "project_settings"
    payload["file_path"] = str(
        ROOT / ".claude/settings.json"
    )

    _, output, _ = run_hook(payload, tmp_path)

    assert output["decision"] == "block"
    assert "immutable" in output["reason"]


def test_specialist_lifecycle_audit_does_not_store_prompt_or_output(
    tmp_path,
):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_specialist_lifecycle_audit_does_not_store_prompt_or_output؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    payload = {
        "session_id": "session-test",
        "cwd": str(ROOT),
        "permission_mode": "dontAsk",
        "hook_event_name": "SubagentStart",
        "agent_type": "specialist-worker",
        "agent_id": "worker-1",
        "prompt": "SECRET_PROMPT_MUST_NOT_BE_STORED",
    }

    _, output, audit_dir = run_hook(payload, tmp_path)

    assert (
        output["hookSpecificOutput"]["hookEventName"]
        == "SubagentStart"
    )

    files = list(audit_dir.rglob("*.json"))
    assert len(files) == 1

    stored = files[0].read_text(encoding="utf-8")
    assert "SECRET_PROMPT_MUST_NOT_BE_STORED" not in stored
    assert "specialist-worker" in stored


def test_runtime_event_directory_is_gitignored():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_event_directory_is_gitignored؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    gitignore = (ROOT / ".gitignore").read_text(
        encoding="utf-8"
    )

    assert ".claude/runtime-events/" in gitignore


def test_runtime_preflight_accepts_hardened_project_mcp_command(
    tmp_path,
):
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_preflight_accepts_hardened_project_mcp_command؛ المدخلات المهمة: tmp_path.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    payload = runtime_payload("UserPromptSubmit")
    payload["prompt"] = "run server 2"

    result, output, _ = run_hook(
        payload,
        tmp_path,
    )

    assert result.returncode == 0
    assert output is not None
    assert "decision" not in output
    assert (
        "preflight passed"
        in output["hookSpecificOutput"]["additionalContext"]
    )


def test_project_mcp_validation_accepts_hardened_argv():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_project_mcp_validation_accepts_hardened_argv؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    hook_source = HOOK.read_text(encoding="utf-8")

    assert "def _valid_project_mcp_command" in hook_source
    assert '"--no-sync"' in hook_source
    assert '"--project"' in hook_source
    assert '"${CLAUDE_PROJECT_DIR:-.}"' in hook_source
