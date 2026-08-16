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
    parser.add_argument("source", help="Knowledge source ID or slug.")
    args = parser.parse_args()

    source_repository = container.knowledge_source_repository

    try:
        source_id = int(args.source)
        source = source_repository.get_by_id(source_id)
    except ValueError:
        source = source_repository.get_by_slug(args.source)

    if source is None:
        raise SystemExit(
            f"Knowledge source not found: {args.source}"
        )

    document = container.knowledge_ingestion_service.ingest_source(
        source.id
    )

    print()
    print("Knowledge source ingested")
    print("=" * 80)
    print(f"Source:          {source.slug} (id={source.id})")
    print(f"Document ID:     {document.id}")
    print(f"Status:          {document.status}")
    print(f"Canonical URI:   {document.canonical_uri}")
    print(f"Title:           {document.title or '—'}")
    print(f"Media type:      {document.media_type or '—'}")
    print(f"Page count:      {document.page_count or '—'}")
    print(f"Characters:      {document.character_count}")
    print(f"Parser:          {document.parser_name or '—'}")
    print(f"Content hash:    {document.content_hash}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
