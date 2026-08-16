"""
أداة تطوير/تشخيص لتشغيل workflow أو فحص contracts والبيانات أثناء التطوير.

الموقع في المعمارية: Developer tooling.
يُستدعى بواسطة: CLI أو المطور مباشرة.
يعتمد مباشرة على: app.composition.
الحد المعماري: ليست application boundary ولا ينبغي اعتبارها API production.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.composition import container


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("report_id", type=int)
    args = parser.parse_args()

    report = container.report_query_service.get_report(args.report_id)
    analysis = container.analysis_repository.get_by_report_id(args.report_id)

    if analysis is None:
        raise SystemExit(f"No analysis exists for report_id={args.report_id}.")

    decision = container.investigation_router.route(
        report=report,
        analysis=analysis,
    )

    investigation = (
        container.investigation_persistence_service.persist_routing_decision(
            server_id=report.server_id,
            report_id=report.id,
            analysis_id=analysis.id,
            decision=decision,
        )
    )

    print()
    print("Investigation persisted")
    print("=" * 72)
    print(f"Investigation ID: {investigation.investigation_id}")
    print(f"Candidates:       {len(investigation.candidates)}")
    print(
        "Selected:         "
        f"{sum(1 for item in investigation.candidates if item.is_selected)}"
    )
    print()
    print(
        "Inspect with:\n"
        "  uv run python tools/dev/inspect_investigation.py "
        f"{investigation.investigation_id}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
