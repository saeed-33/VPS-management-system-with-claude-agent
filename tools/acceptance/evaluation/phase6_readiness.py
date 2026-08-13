from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Phase6Metric(StrEnum):
    CLAUDE_NATIVE_SANDBOX = "claude_native_sandbox"
    FAIL_CLOSED_STARTUP = "fail_closed_startup"
    UNSANDBOXED_ESCAPE_PREVENTION = "unsandboxed_escape_prevention"
    FILESYSTEM_ISOLATION = "filesystem_isolation"
    NETWORK_ISOLATION = "network_isolation"
    MCP_SAFETY = "mcp_safety"
    VALIDATION_EXECUTION = "validation_execution"
    EVIDENCE_COMPLETENESS = "evidence_completeness"
    VERIFICATION_CORRECTNESS = "verification_correctness"
    FINGERPRINT_INTEGRITY = "fingerprint_integrity"
    APPROVAL_GATE = "approval_gate"
    PERSISTENCE_AUDIT = "persistence_audit"
    REAL_SANDBOX_ACCEPTANCE = "real_sandbox_acceptance"


@dataclass(frozen=True, slots=True)
class Phase6Observation:
    metric: Phase6Metric
    numerator: int
    denominator: int
    threshold: float = 1.0
    details: str = ""

    @property
    def score(self) -> float:
        return self.numerator / self.denominator


class Phase6ReadinessGate:
    def evaluate(self, observations: list[Phase6Observation], *, real_acceptance_status: str) -> dict:
        results = []
        blockers = []
        indexed = {item.metric: item for item in observations}
        for metric in Phase6Metric:
            item = indexed.get(metric)
            if item is None:
                blockers.append(f"{metric.value}: observation missing")
                continue
            passed = item.score >= item.threshold
            if metric == Phase6Metric.REAL_SANDBOX_ACCEPTANCE and real_acceptance_status != "PASS":
                passed = False
            results.append({"metric": metric.value, "numerator": item.numerator, "denominator": item.denominator,
                            "score": item.score, "threshold": item.threshold, "passed": passed,
                            "details": item.details})
            if not passed:
                blockers.append(f"{metric.value}: threshold not met")
        if real_acceptance_status == "BLOCKED_BY_SANDBOX_RUNTIME":
            blockers.append("real sandbox acceptance: native sandbox runtime unavailable")
        return {"status": "READY_FOR_SANDBOXED_SUPERVISED_OPERATIONS" if not blockers else "BLOCKED",
                "automatic_remediation_allowed": False, "blocking_reasons": list(dict.fromkeys(blockers)),
                "metrics": results}
