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


def read_text(
    relative_path: str,
) -> str:
    """
    يقرأ أو يعرض state المشروع لتسهيل الفحص ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى read_text؛ المدخلات المهمة: relative_path.
    تعيد str أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    return (
        ROOT
        / relative_path
    ).read_text(
        encoding="utf-8",
    )


def parse_frontmatter(
    text: str,
) -> dict[str, object]:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى parse_frontmatter؛ المدخلات المهمة: text.
    تعيد dict[str, object] أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    assert text.startswith("---\n")

    _, frontmatter, _ = text.split(
        "---",
        2,
    )

    parsed: dict[str, object] = {}
    current_list: str | None = None

    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()

        if not line:
            continue

        if line.startswith("  - "):
            assert current_list is not None
            parsed.setdefault(
                current_list,
                [],
            ).append(
                line[4:]
            )
            continue

        current_list = None

        if line.endswith(":"):
            current_list = line[:-1]
            parsed[current_list] = []
            continue

        key, value = line.split(
            ":",
            1,
        )
        parsed[key] = value.strip()

    return parsed


def test_project_mcp_server_is_registered_for_claude_code():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_project_mcp_server_is_registered_for_claude_code؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    config = json.loads(
        read_text(".mcp.json")
    )

    server = config["mcpServers"]["vps"]

    assert server["command"] == "uv"
    assert server["args"] == [
        "run",
        "--no-sync",
        "--project",
        "${CLAUDE_PROJECT_DIR:-.}",
        "python",
        (
            "${CLAUDE_PROJECT_DIR:-.}/"
            "tools/run_project_mcp_server.py"
        ),
    ]
    assert server["alwaysLoad"] is True


def test_claude_settings_use_enforced_permissions():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_claude_settings_use_enforced_permissions؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    settings = json.loads(
        read_text(".claude/settings.json")
    )

    assert "project" not in settings
    assert "instructions" not in settings
    assert "safety" not in settings

    permissions = settings["permissions"]

    assert "mcp__vps__run_monitoring" in permissions[
        "allow"
    ]
    assert "mcp__vps__run_specialist" in permissions[
        "allow"
    ]
    assert "Bash(ssh *)" in permissions["deny"]
    assert "Bash(psql *)" in permissions["deny"]


def test_claude_agents_have_frontmatter_and_tools():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_claude_agents_have_frontmatter_and_tools؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    agent_paths = [
        ".claude/agents/server-supervisor.md",
        ".claude/agents/specialist-worker.md",
    ]

    for path in agent_paths:
        frontmatter = parse_frontmatter(
            read_text(path)
        )

        assert frontmatter["name"]
        assert frontmatter["description"]
        assert frontmatter["mcpServers"] == [
            "vps",
        ]
        assert frontmatter["model"] == "inherit"
        assert isinstance(
            frontmatter["tools"],
            list,
        )
        assert any(
            str(tool).startswith("mcp__vps__")
            for tool in frontmatter["tools"]
        )


def test_server_supervisor_can_delegate_only_specialist_worker():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_server_supervisor_can_delegate_only_specialist_worker؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    frontmatter = parse_frontmatter(
        read_text(
            ".claude/agents/server-supervisor.md"
        )
    )

    assert "Agent(specialist-worker)" in frontmatter[
        "tools"
    ]
    assert "Agent" not in frontmatter["tools"]
    assert "monitor-server" in frontmatter[
        "skills"
    ]
    assert "analyze-incident" in frontmatter[
        "skills"
    ]
    assert "investigate-incident" in frontmatter[
        "skills"
    ]
    assert "plan-remediation" in frontmatter[
        "skills"
    ]


def test_specialist_worker_cannot_spawn_agents():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_specialist_worker_cannot_spawn_agents؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    frontmatter = parse_frontmatter(
        read_text(
            ".claude/agents/specialist-worker.md"
        )
    )

    assert not any(
        str(tool) == "Agent"
        or str(tool).startswith("Agent(")
        for tool in frontmatter["tools"]
    )


def test_commands_are_not_a_second_workflow_surface():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_commands_are_not_a_second_workflow_surface؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert not (
        ROOT
        / ".claude"
        / "commands"
    ).exists()


def test_global_rules_are_invariants_only():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_global_rules_are_invariants_only؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    rules_dir = (
        ROOT
        / ".claude"
        / "rules"
    )

    rule_names = {
        path.name
        for path in rules_dir.glob("*.md")
    }

    assert rule_names == {
        "safety.md",
        "evidence-grounding.md",
    }


def test_placeholder_hooks_are_not_checked_in():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_placeholder_hooks_are_not_checked_in؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    assert not (
        ROOT
        / ".claude"
        / "hooks"
        / "README.md"
    ).exists()


def test_active_runtime_instructions_do_not_claim_c1_structure_only():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_active_runtime_instructions_do_not_claim_c1_structure_only؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    claude_md = read_text("CLAUDE.md")

    assert "C.1 is structure-only" not in claude_md
    assert "C.14 - Real Claude-Native Orchestration" in claude_md
    assert "Do not recreate `.claude/commands/`" in claude_md
