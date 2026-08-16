"""
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_ALLOW = {
    "mcp__vps__get_server_context",
    "mcp__vps__get_monitoring_profile",
    "mcp__vps__run_monitoring",
    "mcp__vps__get_latest_report",
    "mcp__vps__get_report",
    "mcp__vps__find_exact_report_match",
    "mcp__vps__get_top_similar_reports",
    "mcp__vps__analyze_report",
    "mcp__vps__get_analysis",
    "mcp__vps__start_investigation",
    "mcp__vps__get_investigation",
    "mcp__vps__get_investigation_status",
    "mcp__vps__get_evidence",
    "mcp__vps__get_available_specialists",
    "mcp__vps__get_specialist_definition",
    "mcp__vps__run_specialist",
    "mcp__vps__propose_remediation",
    "mcp__vps__create_remediation_plan",
    "mcp__vps__test_remediation_in_sandbox",
    "mcp__vps__request_user_approval",
    "mcp__vps__apply_approved_remediation",
    "mcp__vps__attempt_autonomous_remediation",
    "Agent(specialist-worker)",
}

FORBIDDEN_REMEDIATION = {
    "mcp__vps__raw_ssh",
    "mcp__vps__raw_shell",
    "mcp__vps__execute_command",
}


def read_text(relative_path: str) -> str:
    """
    يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى read_text؛ المدخلات المهمة: relative_path.
    تعيد str أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return (ROOT / relative_path).read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, object]:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى parse_frontmatter؛ المدخلات المهمة: text.
    تعيد dict[str, object] أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    assert text.startswith("---\n")
    _, fm, _ = text.split("---", 2)

    parsed: dict[str, object] = {}
    current_list: str | None = None

    for raw_line in fm.splitlines():
        line = raw_line.rstrip()

        if not line:
            continue

        if line.startswith("  - "):
            assert current_list is not None
            parsed.setdefault(current_list, []).append(line[4:])
            continue

        current_list = None

        if line.endswith(":"):
            current_list = line[:-1]
            parsed[current_list] = []
            continue

        key, value = line.split(":", 1)
        parsed[key] = value.strip()

    return parsed


def test_settings_allow_only_current_runtime_capabilities():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_settings_allow_only_current_runtime_capabilities؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    settings = json.loads(read_text(".claude/settings.json"))
    assert set(settings["permissions"]["allow"]) == EXPECTED_ALLOW


def test_raw_remediation_escape_tools_are_explicitly_denied():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_raw_remediation_escape_tools_are_explicitly_denied؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    settings = json.loads(read_text(".claude/settings.json"))
    allow = set(settings["permissions"]["allow"])
    deny = set(settings["permissions"]["deny"])

    assert FORBIDDEN_REMEDIATION.isdisjoint(allow)
    assert FORBIDDEN_REMEDIATION <= deny


def test_raw_operational_shell_paths_are_denied_for_both_shells():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_raw_operational_shell_paths_are_denied_for_both_shells؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    settings = json.loads(read_text(".claude/settings.json"))
    deny = set(settings["permissions"]["deny"])

    for tool in ("Bash", "PowerShell"):
        for command in (
            "ssh *",
            "scp *",
            "sftp *",
            "psql *",
            "mysql *",
            "kubectl *",
            "docker exec *",
        ):
            assert f"{tool}({command})" in deny


def test_skill_inline_shell_execution_is_disabled():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_skill_inline_shell_execution_is_disabled؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    settings = json.loads(read_text(".claude/settings.json"))
    assert settings["disableSkillShellExecution"] is True


def test_runtime_agents_use_inherited_model_and_dontask():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_runtime_agents_use_inherited_model_and_dontask؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    for rel in (
        ".claude/agents/server-supervisor.md",
        ".claude/agents/specialist-worker.md",
    ):
        fm = parse_frontmatter(read_text(rel))
        assert fm["model"] == "inherit"
        assert fm["permissionMode"] == "dontAsk"


def test_server_supervisor_uses_supervised_remediation_tools():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_server_supervisor_uses_supervised_remediation_tools؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    fm = parse_frontmatter(
        read_text(".claude/agents/server-supervisor.md")
    )
    tools = set(fm["tools"])

    assert "mcp__vps__propose_remediation" in tools
    assert "mcp__vps__apply_approved_remediation" in tools
    assert FORBIDDEN_REMEDIATION.isdisjoint(tools)


def test_specialist_worker_has_no_remediation_tools():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_specialist_worker_has_no_remediation_tools؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    fm = parse_frontmatter(
        read_text(".claude/agents/specialist-worker.md")
    )
    assert not any("remediation" in tool for tool in fm["tools"])
