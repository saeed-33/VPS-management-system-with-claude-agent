"""
أداة تطوير/تشخيص لتشغيل workflow أو فحص contracts والبيانات أثناء التطوير.

الموقع في المعمارية: Developer tooling.
يُستدعى بواسطة: CLI أو المطور مباشرة.
يعتمد مباشرة على: app.composition.analysis.embedding_factory، app.capabilities.knowledge.retrieval، app.core.config، app.infrastructure.database.repositories.knowledge_retrieval_repository.
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

from app.composition.analysis.embedding_factory import (
    create_embedding_client,
)
from app.capabilities.knowledge.retrieval.retriever import KnowledgeHybridRetriever
from app.core.config import settings
from app.infrastructure.database.repositories.knowledge_retrieval_repository.repository import KnowledgeRetrievalRepository


async def run(args) -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى run؛ المدخلات المهمة: args.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    domains = tuple(
        value.strip().casefold()
        for value in (args.domains or "").split(",")
        if value.strip()
    )

    retriever = KnowledgeHybridRetriever(
        repository=KnowledgeRetrievalRepository(),
        embedding_client=create_embedding_client(settings),
        vector_candidate_limit=args.vector_limit,
        full_text_candidate_limit=args.text_limit,
        top_k=args.top_k,
        rrf_k=args.rrf_k,
        minimum_vector_score=args.minimum_vector_score,
        hnsw_ef_search=settings.rag_hnsw_ef_search,
    )

    contexts = await retriever.retrieve(
        query=args.query,
        specialist_slug=args.specialist,
        domains=domains,
    )

    print()
    print("Knowledge Hybrid Retrieval")
    print("=" * 118)
    print(f"Query:       {args.query}")
    print(f"Specialist:  {args.specialist or '—'}")
    print("Domains:     " + (", ".join(domains) or "—"))
    print(f"Results:     {len(contexts)}")

    if contexts:
        print()
        print(
            f"{'RANK':4} {'SOURCE':25} {'STRATEGY':10} "
            f"{'FUSION':8} {'VECTOR':8} {'TEXT':8} "
            f"{'SECTION':24} PREVIEW"
        )
        print("-" * 150)

        for item in contexts:
            preview = item.content.replace("\n", " ")[:90]

            print(
                f"{item.rank:<4} "
                f"{item.source_slug[:25]:25} "
                f"{item.retrieval_strategy:10} "
                f"{item.fusion_score:<8.5f} "
                f"{(item.vector_score or 0):<8.4f} "
                f"{(item.full_text_score or 0):<8.4f} "
                f"{(item.section_title or '—')[:24]:24} "
                f"{preview}"
            )

    return 0


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--specialist")
    parser.add_argument("--domains")
    parser.add_argument("--top-k", type=int, default=6)
    parser.add_argument("--vector-limit", type=int, default=12)
    parser.add_argument("--text-limit", type=int, default=20)
    parser.add_argument("--rrf-k", type=int, default=60)
    parser.add_argument(
        "--minimum-vector-score",
        type=float,
        default=0.35,
    )
    args = parser.parse_args()

    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
