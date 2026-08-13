from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


SKILLS = {
    "monitor-server": {
        "tools": {
            "mcp__vps__get_server_context",
            "mcp__vps__get_monitoring_profile",
            "mcp__vps__run_monitoring",
            "mcp__vps__get_latest_report",
        },
        "sections": {
            "## Input contract",
            "## Preconditions",
            "## Workflow",
            "## Failure behavior",
            "## Stopping conditions",
            "## Output contract",
        },
    },
    "analyze-incident": {
        "tools": {
            "mcp__vps__get_report",
            "mcp__vps__find_exact_report_match",
            "mcp__vps__get_top_similar_reports",
            "mcp__vps__analyze_report",
            "mcp__vps__get_analysis",
        },
        "sections": {
            "## Input contract",
            "## Preconditions",
            "## Workflow",
            "## Failure behavior",
            "## Stopping conditions",
            "## Output contract",
        },
    },
    "investigate-incident": {
        "tools": {
            "mcp__vps__get_analysis",
            "mcp__vps__start_investigation",
            "mcp__vps__get_investigation",
            "mcp__vps__get_investigation_status",
            "mcp__vps__get_evidence",
            "Agent(specialist-worker)",
        },
        "sections": {
            "## Input contract",
            "## Preconditions",
            "## Workflow",
            "## Failure behavior",
            "## Stopping conditions",
            "## Output contract",
        },
    },
    "plan-remediation": {
        "tools": {
            "mcp__vps__get_investigation",
            "mcp__vps__get_investigation_status",
            "mcp__vps__get_evidence",
            "mcp__vps__propose_remediation",
            "mcp__vps__create_remediation_plan",
            "mcp__vps__test_remediation_in_sandbox",
            "mcp__vps__request_user_approval",
            "mcp__vps__apply_approved_remediation",
        },
        "sections": {
            "## Input contract",
            "## Preconditions",
            "## Workflow",
            "## Failure behavior",
            "## Stopping conditions",
            "## Output contract",
        },
    },
}


def read_skill(name: str) -> str:
    return (
        ROOT
        / ".claude"
        / "skills"
        / name
        / "SKILL.md"
    ).read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    assert text.startswith("---\n")
    _, data, _ = text.split("---", 2)
    return data


def allowed_tools(text: str) -> set[str]:
    data = frontmatter(text)
    tools: set[str] = set()
    in_allowed = False

    for raw in data.splitlines():
        line = raw.rstrip()

        if line == "allowed-tools:":
            in_allowed = True
            continue

        if in_allowed and line.startswith("  - "):
            tools.add(line[4:])
            continue

        if in_allowed and line and not line.startswith(" "):
            in_allowed = False

    return tools


def test_operational_skill_set_is_canonical():
    skill_root = ROOT / ".claude" / "skills"

    names = {
        path.name
        for path in skill_root.iterdir()
        if path.is_dir()
    }

    assert names == set(SKILLS)


def test_skills_have_frontmatter_and_exact_intended_tools():
    for name, contract in SKILLS.items():
        text = read_skill(name)
        fm = frontmatter(text)

        assert f"name: {name}" in fm
        assert "description:" in fm
        assert allowed_tools(text) == contract["tools"]


def test_skills_define_operational_contract_sections():
    for name, contract in SKILLS.items():
        text = read_skill(name)

        for section in contract["sections"]:
            assert section in text, (name, section)


def test_analysis_skill_never_forces_normal_analysis():
    text = read_skill("analyze-incident")

    assert "force = false" in text
    assert "Do not call `force: true`" in text


def test_investigation_skill_preserves_db_specialist_authority():
    text = read_skill("investigate-incident")

    assert "database-defined" in text
    assert "selected_specialists" in text
    assert "Agent(specialist-worker)" in text


def test_remediation_skill_is_supervised_and_approval_gated():
    text = read_skill("plan-remediation")
    tools = allowed_tools(text)

    assert "mcp__vps__propose_remediation" in tools
    assert "mcp__vps__create_remediation_plan" in tools
    assert "mcp__vps__test_remediation_in_sandbox" in tools
    assert "mcp__vps__request_user_approval" in tools
    assert "mcp__vps__apply_approved_remediation" in tools
    assert "persisted human approval" in text


def test_server_supervisor_preloads_canonical_workflow_skills():
    text = (
        ROOT
        / ".claude"
        / "agents"
        / "server-supervisor.md"
    ).read_text(encoding="utf-8")

    for skill_name in SKILLS:
        assert f"  - {skill_name}" in text


def test_specialist_worker_is_not_a_workflow_coordinator():
    text = (
        ROOT
        / ".claude"
        / "agents"
        / "specialist-worker.md"
    ).read_text(encoding="utf-8")

    assert "This agent is a worker, not a coordinator." in text


def test_legacy_skill_names_are_removed():
    legacy = {
        "server-monitoring",
        "incident-analysis",
        "specialist-investigation",
        "remediation-planning",
    }

    for name in legacy:
        assert not (
            ROOT
            / ".claude"
            / "skills"
            / name
        ).exists()
