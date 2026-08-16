"""
جزء من Analysis لتحويل report إلى analysis مع Retrieval وLLM.

الموقع في المعمارية: Application capability / analysis.
يُستدعى بواسطة: MCP أو مسارات ما بعد Monitoring.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا ينفذ SSH أو Investigation أو Remediation.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
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
- The `issues` array is ONLY for adverse conditions requiring
  attention.
- Normal, healthy, successful, or reassuring observations MUST
  NOT be placed in `issues`; put them in `positive_findings`.
- "No failed services", "no recent critical errors", successful
  connectivity, and healthy resource levels are positive
  findings, not issues.
- Do not create an INFO issue for a healthy result. If there
  are no adverse conditions, return `"issues": []`.
- Do not copy a historical diagnosis when current evidence
  differs.
- Provide safe and practical recommendations.
- Do not recommend destructive actions.
- Do not include shell commands which modify the server.
- Mark health status as unknown when evidence is insufficient.
- Keep the summary concise and useful to an administrator.
"""


def build_analysis_prompt(
    report_payload: dict[str, Any],
    historical_cases: list[dict[str, Any]] | None = None,
) -> str:
    """
    يبني DTO أو dependency graph من المدخلات ضمن طبقة Application capability / analysis.

    تُستدعى عندما يصل workflow إلى build_analysis_prompt؛ المدخلات المهمة: report_payload، historical_cases.
    تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    serialized_report = json.dumps(
        report_payload,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    cases = historical_cases or []

    serialized_cases = json.dumps(
        cases,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    if cases:
        historical_section = f"""
Historical cases:

{serialized_cases}

Historical-context rules:
- These cases are previous reports and analyses.
- They are not proof of the current server state.
- Use them to identify recurring patterns only.
- Do not report a historical issue as current unless matching
  evidence exists in the current report.
- `similarity_score` is semantic similarity, not diagnostic
  certainty.
- Source IDs are included for auditability.
"""
    else:
        historical_section = """
Historical cases:

No sufficiently similar historical cases were found.
Analyze the current report independently.
"""

    return f"""
Analyze the following Linux monitoring report.

Interpretation notes:
- Empty output from `systemctl --failed` generally means no
  failed services were found.
- Exit status zero means command execution succeeded, but the
  output may still contain operational warnings.
- A non-zero exit status may indicate command failure,
  missing permissions or an unavailable utility.
- Base every current issue on explicit evidence from the
  current report.
- Recommendations must be non-destructive.
- Do not expose or repeat secrets.
- Do not confuse historical context with current evidence.
- Keep the complete JSON response compact.
- Limit the summary to 120 words.
- Return at most 5 issues.
- Every item in `issues` must describe a real warning or
  critical condition. Do not use `issues` for positive facts.
- Keep each issue description under 100 words.
- Return at most 5 positive findings.
- Return at most 5 recommended actions.

Current monitoring report:

{serialized_report}

{historical_section}

Return the analysis using the required structured format.
"""
