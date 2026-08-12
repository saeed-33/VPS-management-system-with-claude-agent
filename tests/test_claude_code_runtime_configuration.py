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


def test_claude_agents_have_frontmatter_and_tools():
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


def test_monitoring_supervisor_can_delegate_to_agent():
    frontmatter = parse_frontmatter(
        read_text(
            ".claude/agents/monitoring-supervisor.md"
        )
    )

    assert "Agent" in frontmatter["tools"]
    assert "server-monitoring" in frontmatter[
        "skills"
    ]
    assert "incident-analysis" in frontmatter[
        "skills"
    ]
