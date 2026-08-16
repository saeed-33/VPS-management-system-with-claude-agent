"""
أداة تطوير/تشخيص لتشغيل workflow أو فحص contracts والبيانات أثناء التطوير.

الموقع في المعمارية: Developer tooling.
يُستدعى بواسطة: CLI أو المطور مباشرة.
يعتمد مباشرة على: app.composition، app.core.config.
الحد المعماري: ليست application boundary ولا ينبغي اعتبارها API production.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.composition import container
from app.core.config import settings


EXPECTED_INDEXES = {
    "ix_knowledge_chunks_search_vector_gin",
    "ix_knowledge_chunks_embedding_hnsw_cosine",
}


def db_indexes() -> set[str]:
    """
    ينفذ خطوة مساعدة ضمن هذا الملف ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى db_indexes؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد set[str] أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    with psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                  AND tablename = 'knowledge_chunks'
                """
            )
            return {
                row[0]
                for row in cursor.fetchall()
            }


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
        container.knowledge_document_repository
        .get_by_id(args.document_id)
    )

    if document is None:
        raise SystemExit("Knowledge document not found.")

    chunks = tuple(document.chunks)
    embedded = [
        chunk
        for chunk in chunks
        if chunk.embedding is not None
    ]

    indexes = db_indexes()
    missing_indexes = EXPECTED_INDEXES - indexes

    print()
    print("Knowledge Index Snapshot")
    print("=" * 96)
    print(f"Document ID:        {document.id}")
    print(f"Status:             {document.status}")
    print(f"Chunks:             {len(chunks)}")
    print(f"Embedded chunks:    {len(embedded)}")
    print(f"Missing embeddings: {len(chunks) - len(embedded)}")
    print(
        "Search indexes:     "
        f"{len(EXPECTED_INDEXES - missing_indexes)}/{len(EXPECTED_INDEXES)}"
    )

    if chunks:
        print()
        print(
            f"{'INDEX':5} {'EMBEDDED':9} "
            f"{'PROVIDER':10} {'DIMS':5} MODEL"
        )
        print("-" * 96)

        for chunk in chunks:
            print(
                f"{chunk.chunk_index:<5} "
                f"{str(chunk.embedding is not None):9} "
                f"{(chunk.embedding_provider or '—'):10} "
                f"{str(chunk.embedding_dimensions or '—'):5} "
                f"{chunk.embedding_model or '—'}"
            )

    if missing_indexes:
        print()
        print(
            "Missing indexes: "
            + ", ".join(sorted(missing_indexes))
        )
        return 1

    if len(embedded) != len(chunks):
        return 1

    if document.status != "indexed":
        return 1

    print()
    print("Knowledge index acceptance: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
