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
    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--domain"
    )
    group.add_argument(
        "--specialist"
    )

    args = parser.parse_args()

    snapshot = (
        container
        .knowledge_source_registry
        .snapshot()
    )

    sources = snapshot.sources

    if args.domain:
        sources = snapshot.find_by_domain(
            args.domain
        )

    if args.specialist:
        sources = (
            snapshot
            .find_for_specialist(
                args.specialist
            )
        )

    print()
    print("Knowledge Source Registry")
    print("=" * 96)
    print(
        f"Enabled sources: {len(snapshot.sources)}"
    )
    print()
    print(
        f"{'SLUG':24} "
        f"{'TYPE':10} "
        f"{'PRIORITY':8} "
        "DOMAINS / SPECIALISTS"
    )
    print("-" * 96)

    for source in sources:
        scope = (
            "domains="
            + ",".join(
                source.domains
            )
            + " specialists="
            + ",".join(
                source.specialist_slugs
            )
        )

        print(
            f"{source.slug:24} "
            f"{source.source_type:10} "
            f"{source.priority:<8} "
            f"{scope}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
