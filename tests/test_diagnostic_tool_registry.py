import pytest

from app.agent.investigation.diagnostic_tools import (
    DiagnosticToolCall,
    build_default_diagnostic_tool_registry,
)


def registry():
    return build_default_diagnostic_tool_registry()


def test_default_registry_contains_expected_read_only_tools():
    tool_ids = {
        item.tool_id
        for item in registry().definitions
    }

    assert {
        "systemd-status",
        "journal-unit",
        "process-top-cpu",
        "memory-summary",
        "disk-filesystems",
        "network-listeners",
        "nginx-config-test",
    }.issubset(tool_ids)


def test_service_parameter_rejects_shell_injection():
    tool = registry().require(
        "systemd-status"
    )

    with pytest.raises(
        ValueError,
        match="Unsafe service name",
    ):
        tool.render_command(
            {
                "service": (
                    "nginx; rm -rf /"
                )
            }
        )


def test_path_parameter_rejects_shell_injection():
    tool = registry().require(
        "disk-path"
    )

    with pytest.raises(
        ValueError,
        match="Unsafe absolute path",
    ):
        tool.render_command(
            {
                "path": (
                    "/tmp;id"
                )
            }
        )


def test_connect_probe_validates_port():
    tool = registry().require(
        "network-connect"
    )

    with pytest.raises(
        ValueError,
        match="between 1 and 65535",
    ):
        tool.render_command(
            {
                "host": "127.0.0.1",
                "port": 70000,
            }
        )


def test_safe_command_rendering():
    tool = registry().require(
        "journal-unit"
    )

    command = tool.render_command(
        {
            "service": "nginx",
            "lines": 50,
        }
    )

    assert command == (
        "journalctl --no-pager "
        "--output=short-iso -u nginx -n 50"
    )


def test_unknown_arguments_are_rejected():
    tool = registry().require(
        "memory-summary"
    )

    with pytest.raises(
        ValueError,
        match="Unknown tool parameters",
    ):
        tool.render_command(
            {
                "command": "id",
            }
        )


def test_specialist_allowlist_blocks_unassigned_tool():
    call = DiagnosticToolCall(
        tool_id="systemd-status",
        arguments={
            "service": "nginx"
        },
    )

    with pytest.raises(
        PermissionError,
        match="not allowed",
    ):
        registry().render_call(
            call,
            allowed_tool_ids=(
                "network-listeners",
            ),
        )


def test_specialist_allowlist_allows_assigned_tool():
    call = DiagnosticToolCall(
        tool_id="systemd-status",
        arguments={
            "service": "nginx"
        },
    )

    command = registry().render_call(
        call,
        allowed_tool_ids=(
            "systemd-status",
        ),
    )

    assert command.endswith(
        "status nginx"
    )


def test_all_default_tools_are_read_only():
    assert all(
        item.risk.value
        == "read_only"
        for item in registry().definitions
    )
