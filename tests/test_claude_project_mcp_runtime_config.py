import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def test_vps_project_mcp_is_explicitly_approved():
    settings = read_json(
        ROOT / ".claude" / "settings.json"
    )

    enabled = settings.get(
        "enabledMcpjsonServers",
        [],
    )

    assert "vps" in enabled
    assert (
        settings.get(
            "enableAllProjectMcpServers",
            False,
        )
        is False
    )


def test_vps_mcp_launch_is_project_root_stable():
    config = read_json(
        ROOT / ".mcp.json"
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

    assert server["env"]["PYTHONUNBUFFERED"] == "1"
    assert server["env"]["UV_NO_PROGRESS"] == "1"
