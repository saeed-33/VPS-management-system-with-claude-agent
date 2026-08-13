from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app


def status(
    name: str,
    passed: bool,
    detail: str = "",
) -> None:
    suffix = "PASS" if passed else "FAIL"
    print(f"- {name}: {suffix}")

    if detail:
        print(f"  {detail}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 4.19.5 Investigation "
            "Web/API runtime acceptance."
        )
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=25,
    )

    args = parser.parse_args()

    if args.limit < 1 or args.limit > 500:
        raise SystemExit(
            "--limit must be between 1 and 500."
        )

    client = TestClient(app)

    print()
    print(
        "# Phase 4.19.5 "
        "Investigation Web/API Acceptance"
    )
    print()
    print(
        "Application:            REAL FastAPI app"
    )
    print(
        "Database reads:         REAL"
    )
    print(
        "Investigation API:      REAL"
    )
    print(
        "Administration pages:   REAL"
    )
    print(
        "Database writes:        NO"
    )
    print(
        "Specialist execution:   NO"
    )

    checks: dict[str, bool] = {}

    print()
    print("## API LIST")
    print()

    list_response = client.get(
        "/api/investigations",
        params={
            "limit": args.limit,
        },
    )

    checks["api_list_200"] = (
        list_response.status_code == 200
    )

    status(
        "api_list_200",
        checks["api_list_200"],
        f"HTTP {list_response.status_code}",
    )

    rows = []

    if checks["api_list_200"]:
        payload = list_response.json()

        checks["api_list_is_array"] = isinstance(
            payload,
            list,
        )

        status(
            "api_list_is_array",
            checks["api_list_is_array"],
        )

        if isinstance(payload, list):
            rows = payload
            print(
                f"  Investigations returned: "
                f"{len(rows)}"
            )

    else:
        checks["api_list_is_array"] = False
        status(
            "api_list_is_array",
            False,
        )

    print()
    print("## WEB LIST")
    print()

    web_response = client.get(
        "/investigations"
    )

    checks["web_list_200"] = (
        web_response.status_code == 200
    )

    checks["web_list_uses_api"] = (
        "/api/investigations"
        in web_response.text
    )

    status(
        "web_list_200",
        checks["web_list_200"],
        f"HTTP {web_response.status_code}",
    )

    status(
        "web_list_uses_api",
        checks["web_list_uses_api"],
    )

    if not rows:
        print()
        print("## LIVE DETAIL")
        print()
        print(
            "No persisted Investigation was "
            "returned by the real database."
        )
        print(
            "List/API/Web routing is valid, "
            "but Phase 4.19 cannot receive "
            "full runtime-detail acceptance "
            "without one persisted Investigation."
        )

        checks[
            "persisted_investigation_available"
        ] = False

        status(
            "persisted_investigation_available",
            False,
        )

        print()
        print("## ACCEPTANCE RESULT")
        print()
        print(
            "Phase 4.19.5: INCOMPLETE "
            "(no persisted Investigation)"
        )

        return 2

    first = rows[0]

    investigation_id = first.get(
        "investigation_id"
    )

    checks[
        "persisted_investigation_available"
    ] = bool(
        investigation_id
    )

    status(
        "persisted_investigation_available",
        checks[
            "persisted_investigation_available"
        ],
        str(investigation_id or "—"),
    )

    if not investigation_id:
        return 2

    print()
    print("## LIVE DETAIL")
    print()
    print(
        f"Investigation ID:       "
        f"{investigation_id}"
    )
    print(
        f"Server ID:              "
        f"{first.get('server_id', '—')}"
    )
    print(
        f"Report ID:              "
        f"{first.get('report_id', '—')}"
    )
    print(
        f"Status:                 "
        f"{first.get('status', '—')}"
    )
    print(
        f"Runtime available:      "
        f"{first.get('runtime_available', False)}"
    )
    print(
        f"Final diagnosis:        "
        f"{first.get('final_diagnosis_available', False)}"
    )

    detail_response = client.get(
        "/api/investigations/"
        + str(investigation_id)
    )

    checks["api_detail_200"] = (
        detail_response.status_code == 200
    )

    status(
        "api_detail_200",
        checks["api_detail_200"],
        f"HTTP {detail_response.status_code}",
    )

    detail = None

    if checks["api_detail_200"]:
        detail = detail_response.json()

    checks["api_identity_consistent"] = (
        isinstance(detail, dict)
        and detail.get(
            "investigation_id"
        )
        == investigation_id
    )

    status(
        "api_identity_consistent",
        checks["api_identity_consistent"],
    )

    checks["api_report_consistent"] = (
        isinstance(detail, dict)
        and detail.get(
            "report_id"
        )
        == first.get(
            "report_id"
        )
    )

    status(
        "api_report_consistent",
        checks["api_report_consistent"],
    )

    web_detail_response = client.get(
        "/investigations/"
        + str(investigation_id)
    )

    checks["web_detail_200"] = (
        web_detail_response.status_code
        == 200
    )

    checks[
        "web_detail_contains_identity"
    ] = (
        str(investigation_id)
        in web_detail_response.text
    )

    checks[
        "web_detail_uses_detail_api"
    ] = (
        "/api/investigations/"
        in web_detail_response.text
    )

    status(
        "web_detail_200",
        checks["web_detail_200"],
        f"HTTP "
        f"{web_detail_response.status_code}",
    )

    status(
        "web_detail_contains_identity",
        checks[
            "web_detail_contains_identity"
        ],
    )

    status(
        "web_detail_uses_detail_api",
        checks[
            "web_detail_uses_detail_api"
        ],
    )

    report_id = first.get(
        "report_id"
    )

    report_response = client.get(
        f"/api/reports/"
        f"{report_id}/investigations"
    )

    checks[
        "report_investigations_200"
    ] = (
        report_response.status_code
        == 200
    )

    status(
        "report_investigations_200",
        checks[
            "report_investigations_200"
        ],
        f"HTTP "
        f"{report_response.status_code}",
    )

    report_rows = []

    if checks[
        "report_investigations_200"
    ]:
        report_rows = (
            report_response.json()
        )

    checks[
        "report_contains_investigation"
    ] = (
        isinstance(
            report_rows,
            list,
        )
        and any(
            row.get(
                "investigation_id"
            )
            == investigation_id
            for row
            in report_rows
            if isinstance(
                row,
                dict,
            )
        )
    )

    status(
        "report_contains_investigation",
        checks[
            "report_contains_investigation"
        ],
    )

    if isinstance(detail, dict):
        runtime_available = bool(
            detail.get(
                "runtime_available"
            )
        )

        runtime = detail.get(
            "runtime"
        )

        checks[
            "runtime_availability_consistent"
        ] = (
            (
                runtime_available
                and isinstance(
                    runtime,
                    dict,
                )
            )
            or (
                not runtime_available
                and runtime is None
            )
        )

        status(
            "runtime_availability_consistent",
            checks[
                "runtime_availability_consistent"
            ],
        )

        if runtime_available:
            print()
            print(
                "## PERSISTED RUNTIME SNAPSHOT"
            )
            print()

            print(
                f"Orchestrator:           "
                f"{runtime.get('orchestrator', '—')}"
            )
            print(
                f"Execution mode:         "
                f"{runtime.get('execution_mode', '—')}"
            )
            print(
                f"Specialist runs:        "
                f"{len(runtime.get('specialist_runs') or [])}"
            )
            print(
                f"Evidence items:         "
                f"{len(runtime.get('evidence') or [])}"
            )
            print(
                f"Correlated claims:      "
                f"{len(runtime.get('correlated_claims') or [])}"
            )
            print(
                f"Conflicts:              "
                f"{len(runtime.get('conflicts') or [])}"
            )

            final_available = bool(
                detail.get(
                    "final_diagnosis_available"
                )
            )

            final_diagnosis = (
                runtime.get(
                    "final_diagnosis"
                )
            )

            checks[
                "final_diagnosis_availability_consistent"
            ] = (
                (
                    final_available
                    and isinstance(
                        final_diagnosis,
                        dict,
                    )
                )
                or (
                    not final_available
                    and final_diagnosis
                    is None
                )
            )

            status(
                "final_diagnosis_availability_consistent",
                checks[
                    "final_diagnosis_availability_consistent"
                ],
            )

            evidence_ids = {
                item.get(
                    "evidence_id"
                )
                for item
                in (
                    runtime.get(
                        "evidence"
                    )
                    or []
                )
                if isinstance(
                    item,
                    dict,
                )
                and item.get(
                    "evidence_id"
                )
            }

            claim_evidence_ids = {
                evidence_id
                for claim
                in (
                    runtime.get(
                        "correlated_claims"
                    )
                    or []
                )
                if isinstance(
                    claim,
                    dict,
                )
                for evidence_id
                in (
                    claim.get(
                        "evidence_ids"
                    )
                    or []
                )
            }

            conflict_evidence_ids = {
                evidence_id
                for conflict
                in (
                    runtime.get(
                        "conflicts"
                    )
                    or []
                )
                if isinstance(
                    conflict,
                    dict,
                )
                for evidence_id
                in (
                    conflict.get(
                        "evidence_ids"
                    )
                    or []
                )
            }

            checks[
                "claim_evidence_trace_valid"
            ] = (
                claim_evidence_ids
                <= evidence_ids
            )

            checks[
                "conflict_evidence_trace_valid"
            ] = (
                conflict_evidence_ids
                <= evidence_ids
            )

            status(
                "claim_evidence_trace_valid",
                checks[
                    "claim_evidence_trace_valid"
                ],
            )

            status(
                "conflict_evidence_trace_valid",
                checks[
                    "conflict_evidence_trace_valid"
                ],
            )

        else:
            checks[
                "final_diagnosis_availability_consistent"
            ] = (
                not detail.get(
                    "final_diagnosis_available"
                )
            )

            checks[
                "claim_evidence_trace_valid"
            ] = True

            checks[
                "conflict_evidence_trace_valid"
            ] = True

            status(
                "final_diagnosis_availability_consistent",
                checks[
                    "final_diagnosis_availability_consistent"
                ],
                "No runtime snapshot persisted.",
            )
            status(
                "claim_evidence_trace_valid",
                True,
                "Not applicable without runtime snapshot.",
            )
            status(
                "conflict_evidence_trace_valid",
                True,
                "Not applicable without runtime snapshot.",
            )
    else:
        checks[
            "runtime_availability_consistent"
        ] = False
        checks[
            "final_diagnosis_availability_consistent"
        ] = False
        checks[
            "claim_evidence_trace_valid"
        ] = False
        checks[
            "conflict_evidence_trace_valid"
        ] = False

    print()
    print("## ACCEPTANCE RESULT")
    print()

    for name, passed in checks.items():
        if name in {
            "api_list_200",
            "api_list_is_array",
            "web_list_200",
            "web_list_uses_api",
            "persisted_investigation_available",
            "api_detail_200",
            "api_identity_consistent",
            "api_report_consistent",
            "web_detail_200",
            "web_detail_contains_identity",
            "web_detail_uses_detail_api",
            "report_investigations_200",
            "report_contains_investigation",
            "runtime_availability_consistent",
            "final_diagnosis_availability_consistent",
            "claim_evidence_trace_valid",
            "conflict_evidence_trace_valid",
        }:
            continue

    passed = all(
        checks.values()
    )

    print(
        "Phase 4.19.5: "
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

    print()
    print(
        "NOTE: This acceptance performs "
        "read-only HTTP requests against "
        "the real application and persisted "
        "Investigation data."
    )

    return (
        0
        if passed
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
