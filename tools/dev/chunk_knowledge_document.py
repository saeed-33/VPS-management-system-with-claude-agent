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
    parser.add_argument("document_id", type=int)
    args = parser.parse_args()

    document = (
        container.knowledge_chunking_service
        .chunk_document(args.document_id)
    )

    print()
    print("Knowledge document chunked")
    print("=" * 88)
    print(f"Document ID:   {document.id}")
    print(f"Source ID:     {document.source_id}")
    print(f"Status:        {document.status}")
    print(f"Characters:    {document.character_count}")
    print(f"Chunks:        {len(document.chunks)}")

    if document.chunks:
        print()
        print(
            f"{'INDEX':5} {'CHARS':7} {'PAGE':6} "
            f"{'SECTION':30} PREVIEW"
        )
        print("-" * 110)

        for chunk in document.chunks:
            preview = chunk.content.replace("\n", " ")[:80]
            print(
                f"{chunk.chunk_index:<5} "
                f"{chunk.character_count:<7} "
                f"{str(chunk.page_number or '-'):6} "
                f"{(chunk.section_title or '—')[:30]:30} "
                f"{preview}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
