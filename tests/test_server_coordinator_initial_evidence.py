from app.domain.investigation.contracts import EvidenceKind
from app.domain.investigation.server_coordinator import ServerCoordinator


def test_initial_connection_failure_becomes_citable_analysis_evidence():
    evidence = ServerCoordinator._analysis_evidence(
        report_id=807,
        analysis_id=638,
        summary="SSH connection failed.",
        issues=(
            {
                "title": "Connection failure",
                "description": (
                    "OSError: [Errno 10013] Connect call failed "
                    "('192.168.127.142', 22)"
                ),
            },
        ),
    )

    assert len(evidence) == 2

    summary = evidence[0]
    issue = evidence[1]

    assert summary.evidence_id == "analysis:638:summary"
    assert summary.kind == EvidenceKind.ANALYSIS

    assert issue.evidence_id == "analysis:638:issue:1"
    assert issue.kind == EvidenceKind.ANALYSIS
    assert "Connect call failed" in issue.excerpt
    assert issue.metadata["issue_index"] == 0


def test_empty_initial_analysis_produces_no_evidence():
    evidence = ServerCoordinator._analysis_evidence(
        report_id=1,
        analysis_id=None,
        summary=None,
        issues=(),
    )

    assert evidence == ()
