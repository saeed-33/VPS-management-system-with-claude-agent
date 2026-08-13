from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, object]:
    assert text.startswith("---\n")
    _, frontmatter, _ = text.split("---", 2)

    parsed: dict[str, object] = {}
    current_list: str | None = None

    for raw_line in frontmatter.splitlines():
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


def test_canonical_agent_set_is_two_bounded_roles():
    agents = ROOT / ".claude" / "agents"
    names = {
        path.name
        for path in agents.glob("*.md")
    }

    assert names == {
        "server-supervisor.md",
        "specialist-worker.md",
    }


def test_server_supervisor_is_main_session_coordinator():
    text = read_text(
        ".claude/agents/server-supervisor.md"
    )
    fm = parse_frontmatter(text)

    assert fm["name"] == "server-supervisor"
    assert fm["model"] == "inherit"
    assert fm["mcpServers"] == ["vps"]

    tools = set(fm["tools"])
    assert "Agent(specialist-worker)" in tools
    assert "Agent" not in tools
    assert "mcp__vps__run_specialist" not in tools
    assert "mcp__vps__apply_approved_remediation" in tools

    assert set(fm["skills"]) == {
        "monitor-server",
        "analyze-incident",
        "investigate-incident",
        "plan-remediation",
    }

    assert "exactly one persisted server" in text
    assert "The only project subagent type" in text
    assert "Do not continue into production remediation." in text


def test_specialist_worker_cannot_delegate_or_remediate():
    text = read_text(
        ".claude/agents/specialist-worker.md"
    )
    fm = parse_frontmatter(text)

    assert fm["name"] == "specialist-worker"
    assert fm["model"] == "inherit"
    assert fm["mcpServers"] == ["vps"]

    tools = set(fm["tools"])
    assert not any(
        tool == "Agent"
        or tool.startswith("Agent(")
        for tool in tools
    )
    assert "mcp__vps__run_specialist" in tools
    assert not any(
        "remediation" in tool
        for tool in tools
    )

    assert "This worker must never spawn another agent." in text
    assert "DB-backed Specialist definition is authoritative" in text


def test_server_supervisor_has_no_raw_execution_tools():
    fm = parse_frontmatter(
        read_text(
            ".claude/agents/server-supervisor.md"
        )
    )

    tools = set(fm["tools"])

    assert not any(
        tool.startswith("Bash")
        or tool.startswith("PowerShell")
        for tool in tools
    )


def test_specialist_worker_has_no_raw_execution_tools():
    fm = parse_frontmatter(
        read_text(
            ".claude/agents/specialist-worker.md"
        )
    )

    tools = set(fm["tools"])

    assert not any(
        tool.startswith("Bash")
        or tool.startswith("PowerShell")
        for tool in tools
    )


def test_investigation_skill_delegates_only_specialist_worker():
    text = read_text(
        ".claude/skills/investigate-incident/SKILL.md"
    )

    fm = parse_frontmatter(text)
    tools = set(fm["allowed-tools"])

    assert "Agent(specialist-worker)" in tools
    assert "mcp__vps__run_specialist" not in tools
    assert "selected_specialists" in text
    assert "sequential Specialist delegation" in text


def test_legacy_agent_files_are_removed():
    for filename in (
        "monitoring-supervisor.md",
        "investigation-coordinator.md",
        "generic-specialist.md",
    ):
        assert not (
            ROOT
            / ".claude"
            / "agents"
            / filename
        ).exists()
