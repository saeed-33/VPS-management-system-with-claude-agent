import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(
    relative_path: str,
) -> str:
    return (
        ROOT
        / relative_path
    ).read_text(
        encoding="utf-8",
    )


def parse_frontmatter(
    text: str,
) -> dict[str, object]:
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
    config = json.loads(
        read_text(".mcp.json")
    )

    server = config["mcpServers"]["vps"]

    assert server["command"] == "uv"
    assert server["args"] == [
        "run",
        "python",
        "tools/run_project_mcp_server.py",
    ]
    assert server["alwaysLoad"] is True


def test_claude_settings_use_enforced_permissions():
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


def test_transitional_agents_have_real_frontmatter_and_project_tools():
    agent_paths = [
        ".claude/agents/monitoring-supervisor.md",
        ".claude/agents/investigation-coordinator.md",
        ".claude/agents/generic-specialist.md",
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
        assert isinstance(
            frontmatter["tools"],
            list,
        )
        assert any(
            str(tool).startswith("mcp__vps__")
            for tool in frontmatter["tools"]
        )


def test_commands_are_not_a_second_workflow_surface():
    assert not (
        ROOT
        / ".claude"
        / "commands"
    ).exists()


def test_global_rules_are_invariants_only():
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
    assert not (
        ROOT
        / ".claude"
        / "hooks"
        / "README.md"
    ).exists()


def test_active_runtime_instructions_do_not_claim_c1_structure_only():
    claude_md = read_text("CLAUDE.md")

    assert "C.1 is structure-only" not in claude_md
    assert "C.14 - Real Claude-Native Orchestration" in claude_md
    assert "Do not recreate `.claude/commands/`" in claude_md
