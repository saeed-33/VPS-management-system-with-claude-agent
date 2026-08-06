import json
from typing import Any


SYSTEM_PROMPT = """
You are a senior Linux systems reliability engineer.

Analyze monitoring reports collected from Linux servers.

Your responsibilities:
- Assess availability, CPU, memory, storage, processes,
  services, network activity, system errors and security
  indicators.
- Correlate evidence across multiple command outputs.
- Distinguish harmless empty output from actual failure.
- Never invent metrics, incidents or root causes.
- Use only evidence contained in the current report and the
  explicitly supplied historical cases.
- Treat historical cases as context, not as proof of the
  current server state.
- Every current issue must be supported by evidence from the
  current report.
- Do not copy a historical diagnosis when the current evidence
  differs.
- Provide safe and practical recommendations.
- Do not recommend destructive actions.
- Do not include shell commands which modify the server.
- Mark the health status as unknown when evidence is
  insufficient.
- Keep the summary concise and useful to an administrator.
"""


def build_analysis_prompt(
    report_payload: dict[str, Any],
    historical_cases: list[dict[str, Any]] | None = None,
) -> str:
    serialized_report = json.dumps(
        report_payload,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    return f"""
Analyze the following Linux monitoring report.

Interpretation notes:
- Empty output from `systemctl --failed` generally means
  that no failed services were found.
- Exit status zero means command execution succeeded, but
  the output can still contain operational warnings.
- A non-zero exit status may indicate command failure,
  missing permissions or an unavailable utility.
- Base every issue on explicit evidence.
- Recommendations must be non-destructive.
- Do not expose or repeat secrets if any appear in output.

Monitoring report:

{serialized_report}
"""