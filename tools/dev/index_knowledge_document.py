"""
أداة تطوير/تشخيص لتشغيل workflow أو فحص contracts والبيانات أثناء التطوير.

الموقع في المعمارية: Developer tooling.
يُستدعى بواسطة: CLI أو المطور مباشرة.
يعتمد مباشرة على: app.capabilities.analysis.retrieval.embedding_factory، app.capabilities.knowledge.indexer، app.composition، app.core.config.
الحد المعماري: ليست application boundary ولا ينبغي اعتبارها API production.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.capabilities.analysis.retrieval.embedding_factory import (
    create_embedding_client,
)
from app.capabilities.knowledge.indexer.indexer import KnowledgeIndexer
from app.composition import container
from app.core.config import settings


async def run(
    *,
    document_id: int,
    force: bool,
) -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى run؛ المدخلات المهمة: document_id، force.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    indexer = KnowledgeIndexer(
        document_repository=container.knowledge_document_repository,
        embedding_client=create_embedding_client(settings),
    )

    result = await indexer.index_document(
        document_id,
        force=force,
    )

    print()
    print("Knowledge document indexed")
    print("=" * 88)
    print(f"Document ID:    {result.document_id}")
    print(f"Status:         {result.status}")
    print(f"Total chunks:   {result.total_chunks}")
    print(f"Indexed now:    {result.indexed_chunks}")
    print(f"Skipped:        {result.skipped_chunks}")
    print(f"Provider:       {result.provider}")
    print(f"Model:          {result.model}")
    print(f"Dimensions:     {result.dimensions}")

    return 0


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("document_id", type=int)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    return asyncio.run(
        run(
            document_id=args.document_id,
            force=args.force,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
