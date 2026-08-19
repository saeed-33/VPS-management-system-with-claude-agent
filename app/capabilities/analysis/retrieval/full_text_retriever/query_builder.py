"""بناء استعلامات البحث النصي من التقرير المنظم."""
from __future__ import annotations

import json

class FullTextQueryBuilder:
    """
    يستخرج من التقرير الحقول النصية الأكثر فائدة لبناء استعلام البحث الكامل.
    """
    def build(self, normalized_report: str) -> str:
        """
        يفك التقرير المنظم ويجمع رسالة الخطأ وحقول التنفيذ النصية في استعلام محدود الحجم.
        """
        try:
            payload = json.loads(normalized_report)
        except (TypeError, ValueError):
            return normalized_report[:10_000]

        terms: list[str] = []

        report_error = payload.get("error_message")
        if report_error:
            terms.append(str(report_error))

        for execution in payload.get("executions", []):
            for field in (
                "command_name",
                "command_text",
                "error_message",
                "stderr",
            ):
                value = execution.get(field)
                if value:
                    terms.append(str(value))

        return "\n".join(terms).strip()[:10_000]
