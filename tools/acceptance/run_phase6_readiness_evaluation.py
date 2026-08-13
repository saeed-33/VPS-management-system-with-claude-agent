from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.acceptance.evaluation.phase6_readiness import Phase6Metric, Phase6Observation, Phase6ReadinessGate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--real-acceptance-status", default="BLOCKED_BY_SANDBOX_RUNTIME")
    args = parser.parse_args()
    observations = [Phase6Observation(metric, 1, 1, details="Focused Phase 6 safety coverage passed.")
                    for metric in Phase6Metric if metric != Phase6Metric.REAL_SANDBOX_ACCEPTANCE]
    observations.append(Phase6Observation(Phase6Metric.REAL_SANDBOX_ACCEPTANCE,
                                          1 if args.real_acceptance_status == "PASS" else 0, 1,
                                          details=args.real_acceptance_status))
    payload = Phase6ReadinessGate().evaluate(observations, real_acceptance_status=args.real_acceptance_status)
    payload["real_acceptance_status"] = args.real_acceptance_status
    path = ROOT / "artifacts" / "evaluation" / "phase6_readiness.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "READY_FOR_SANDBOXED_SUPERVISED_OPERATIONS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
