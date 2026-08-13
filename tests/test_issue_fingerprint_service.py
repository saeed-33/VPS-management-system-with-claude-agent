from dataclasses import dataclass

from app.capabilities.remediation.issue_fingerprint_service import IssueFingerprintService


@dataclass
class Runtime:
    correlated_claims: tuple[dict, ...]
    final_diagnosis: dict | None


@dataclass
class Investigation:
    runtime: Runtime | None
    final_diagnosis_available: bool


class ReadService:
    def __init__(self, investigations):
        self.investigations = investigations

    def get(self, investigation_id):
        return self.investigations.get(investigation_id)


def investigation(*, title="Nginx service inactive", certainty="confirmed", state="inactive", narrative="first wording", claim_id="c1", evidence_id="e1", confidence=0.9, reverse=False, extra_claim=False):
    claims = [
        {
            "claim_id": claim_id,
            "title": title,
            "description": narrative,
            "certainty": certainty,
            "confidence": confidence,
            "evidence_ids": [evidence_id],
            "metadata": {"diagnostic_states": [state]},
        }
    ]
    if extra_claim:
        claims.append({
            "claim_id": "second-claim",
            "title": "Nginx configuration valid",
            "description": "different narrative",
            "certainty": "likely",
            "confidence": 0.4,
            "evidence_ids": ["second-evidence"],
            "metadata": {"diagnostic_states": ["configured"]},
        })
    if reverse:
        claims.reverse()
    return Investigation(Runtime(tuple(claims), {"summary": narrative}), True)


def test_equivalent_persisted_diagnoses_have_same_fingerprint():
    read = ReadService({
        "a": investigation(claim_id="claim-a", evidence_id="evidence-a", narrative="one", confidence=0.8),
        "b": investigation(claim_id="claim-b", evidence_id="evidence-b", narrative="two", confidence=0.95),
        "c": investigation(claim_id="claim-c", evidence_id="evidence-c", narrative="three", confidence=0.2),
    })
    service = IssueFingerprintService(investigation_read_service=read)
    assert service.derive("a") == service.derive("b") == service.derive("c")


def test_semantic_change_changes_fingerprint():
    read = ReadService({"a": investigation(), "b": investigation(state="failed")})
    service = IssueFingerprintService(investigation_read_service=read)
    assert service.derive("a") != service.derive("b")


def test_claim_order_does_not_change_fingerprint():
    first = investigation(extra_claim=True)
    second = investigation(extra_claim=True)
    second.runtime.correlated_claims = tuple(reversed(second.runtime.correlated_claims))
    read = ReadService({"a": first, "b": second})
    service = IssueFingerprintService(investigation_read_service=read)
    assert service.derive("a") == service.derive("b")


def test_unavailable_diagnosis_returns_none():
    read = ReadService({"a": Investigation(None, False), "b": Investigation(Runtime((), None), True)})
    service = IssueFingerprintService(investigation_read_service=read)
    assert service.derive("a") is None
    assert service.derive("b") is None
