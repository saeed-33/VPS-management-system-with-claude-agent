import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from app.domain.investigation.contracts import EvidenceKind
from app.domain.investigation.diagnostic_policy import (
    DiagnosticPolicyDecision,
    DiagnosticPolicyReason,
    DiagnosticPolicyResult,
)
from app.domain.investigation.evidence_collection import (
    DiagnosticExecutionOutcome,
    EvidenceCollectionRequest,
    EvidenceCollectionService,
)


class Repository:
    def __init__(self, server="default"):
        self.calls = 0
        if server == "default":
            self.server = SimpleNamespace(
                id=7,
                host="192.0.2.10",
                port=22,
                username="ubuntu",
                private_key_path=None,
            )
        else:
            self.server = server

    def get_by_id(self, server_id):
        self.calls += 1
        if self.server is None:
            return None
        if self.server.id != server_id:
            return None
        return self.server


class Runner:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = 0
        self.last_config = None
        self.last_command = None

    async def run(
        self,
        *,
        config,
        tool_id,
        command_text,
        timeout_seconds,
    ):
        self.calls += 1
        self.last_config = config
        self.last_command = command_text
        return self.outcome


def make_outcome(
    *,
    success=True,
    exit_status=0,
    stdout="active (running)",
    stderr="",
    error_message=None,
):
    timestamp = datetime.now(UTC)
    return DiagnosticExecutionOutcome(
        success=success,
        exit_status=exit_status,
        stdout=stdout,
        stderr=stderr,
        error_message=error_message,
        started_at=timestamp,
        finished_at=timestamp,
        duration_ms=12.5,
    )


def allowed_policy(output_limit_chars=20000):
    return DiagnosticPolicyResult(
        decision=DiagnosticPolicyDecision.ALLOW,
        reasons=(DiagnosticPolicyReason.ALLOWED,),
        specialist_slug="nginx",
        tool_id="systemd-status",
        rendered_command=(
            "systemctl --no-pager --full status nginx"
        ),
        timeout_seconds=12,
        output_limit_chars=output_limit_chars,
        metadata={
            "risk": "read_only",
            "requires_sudo": False,
        },
    )


def denied_policy():
    return DiagnosticPolicyResult(
        decision=DiagnosticPolicyDecision.DENY,
        reasons=(
            DiagnosticPolicyReason.TOOL_NOT_ALLOWED,
        ),
        specialist_slug="nginx",
        tool_id="systemd-status",
    )


def make_service(
    *,
    repository=None,
    runner=None,
):
    repository = repository or Repository()
    runner = runner or Runner(make_outcome())

    return (
        EvidenceCollectionService(
            server_repository=repository,
            default_private_key_path="/keys/default",
            known_hosts_path="/keys/known_hosts",
            connection_timeout_seconds=10,
            runner=runner,
        ),
        repository,
        runner,
    )


def test_denied_policy_never_touches_repository_or_runner():
    collector, repository, runner = make_service()

    with pytest.raises(PermissionError):
        asyncio.run(
            collector.collect(
                EvidenceCollectionRequest(
                    evidence_id="ev-1",
                    server_id=7,
                    policy_result=denied_policy(),
                )
            )
        )

    assert repository.calls == 0
    assert runner.calls == 0


def test_success_becomes_command_result_evidence():
    collector, _, runner = make_service()

    evidence = asyncio.run(
        collector.collect(
            EvidenceCollectionRequest(
                evidence_id="ev-1",
                server_id=7,
                policy_result=allowed_policy(),
            )
        )
    )

    assert evidence.kind == EvidenceKind.COMMAND_RESULT
    assert evidence.source_id == 7
    assert "active (running)" in evidence.excerpt
    assert evidence.metadata["success"] is True
    assert evidence.metadata["exit_status"] == 0
    assert evidence.metadata["tool_id"] == "systemd-status"
    assert runner.calls == 1


def test_nonzero_command_is_still_evidence():
    runner = Runner(
        make_outcome(
            success=False,
            exit_status=3,
            stdout="inactive",
            stderr="unit failed",
            error_message=(
                "Command returned a non-zero exit status."
            ),
        )
    )
    collector, _, _ = make_service(runner=runner)

    evidence = asyncio.run(
        collector.collect(
            EvidenceCollectionRequest(
                evidence_id="ev-failed",
                server_id=7,
                policy_result=allowed_policy(),
            )
        )
    )

    assert evidence.metadata["success"] is False
    assert evidence.metadata["exit_status"] == 3
    assert "unit failed" in evidence.excerpt


def test_output_is_truncated_to_policy_limit():
    runner = Runner(
        make_outcome(stdout="x" * 500)
    )
    collector, _, _ = make_service(runner=runner)

    evidence = asyncio.run(
        collector.collect(
            EvidenceCollectionRequest(
                evidence_id="ev-long",
                server_id=7,
                policy_result=allowed_policy(
                    output_limit_chars=120
                ),
            )
        )
    )

    assert len(evidence.excerpt) <= 120
    assert evidence.metadata["excerpt_truncated"] is True


def test_server_specific_key_overrides_default():
    repository = Repository(
        SimpleNamespace(
            id=7,
            host="192.0.2.10",
            port=2222,
            username="ubuntu",
            private_key_path="/keys/server-specific",
        )
    )
    runner = Runner(make_outcome())
    collector, _, _ = make_service(
        repository=repository,
        runner=runner,
    )

    asyncio.run(
        collector.collect(
            EvidenceCollectionRequest(
                evidence_id="ev-key",
                server_id=7,
                policy_result=allowed_policy(),
            )
        )
    )

    assert (
        runner.last_config.private_key_path
        == "/keys/server-specific"
    )
    assert runner.last_config.port == 2222


def test_default_key_is_used_when_server_has_none():
    collector, _, runner = make_service()

    asyncio.run(
        collector.collect(
            EvidenceCollectionRequest(
                evidence_id="ev-default",
                server_id=7,
                policy_result=allowed_policy(),
            )
        )
    )

    assert runner.last_config.private_key_path == "/keys/default"


def test_missing_server_does_not_call_runner():
    repository = Repository(None)
    runner = Runner(make_outcome())
    collector, _, _ = make_service(
        repository=repository,
        runner=runner,
    )

    with pytest.raises(
        ValueError,
        match="was not found",
    ):
        asyncio.run(
            collector.collect(
                EvidenceCollectionRequest(
                    evidence_id="ev-missing",
                    server_id=99,
                    policy_result=allowed_policy(),
                )
            )
        )

    assert runner.calls == 0


def test_connection_failure_becomes_evidence():
    runner = Runner(
        make_outcome(
            success=False,
            exit_status=None,
            stdout="",
            stderr="",
            error_message=(
                "OSError: connection refused"
            ),
        )
    )
    collector, _, _ = make_service(runner=runner)

    evidence = asyncio.run(
        collector.collect(
            EvidenceCollectionRequest(
                evidence_id="ev-connect",
                server_id=7,
                policy_result=allowed_policy(),
            )
        )
    )

    assert evidence.metadata["success"] is False
    assert evidence.metadata["exit_status"] is None
    assert "connection refused" in evidence.excerpt


def test_empty_output_is_explicit():
    runner = Runner(
        make_outcome(
            stdout="",
            stderr="",
            error_message=None,
        )
    )
    collector, _, _ = make_service(runner=runner)

    evidence = asyncio.run(
        collector.collect(
            EvidenceCollectionRequest(
                evidence_id="ev-empty",
                server_id=7,
                policy_result=allowed_policy(),
            )
        )
    )

    assert evidence.excerpt == (
        "(command produced no output)"
    )
