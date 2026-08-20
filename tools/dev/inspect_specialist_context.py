"""
أداة تطوير/تشخيص لتشغيل workflow أو فحص contracts والبيانات أثناء التطوير.

الموقع في المعمارية: Developer tooling.
يُستدعى بواسطة: CLI أو المطور مباشرة.
يعتمد مباشرة على: app.composition.analysis.embedding_factory، app.core.contracts.investigation، app.capabilities.knowledge.retrieval، app.capabilities.investigation.specialist_context، app.composition، app.core.config.
الحد المعماري: ليست application boundary ولا ينبغي اعتبارها API production.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import argparse
import asyncio
from uuid import uuid4
import sys
from pathlib import Path

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from app.composition.analysis.embedding_factory import (
    create_embedding_client,
)
from app.core.contracts.investigation.specialist_task import SpecialistTask
from app.capabilities.knowledge.retrieval.retriever import KnowledgeHybridRetriever
from app.capabilities.investigation.specialist_context.specialist_context_builder import SpecialistContextBuilder
from app.composition import container
from app.core.config import settings
from app.infrastructure.database.repositories.knowledge_retrieval_repository.repository import KnowledgeRetrievalRepository


async def run(args) -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى run؛ المدخلات المهمة: args.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    specialist = (
        container
        .specialist_registry
        .get_by_slug(
            args.specialist
        )
    )

    if specialist is None:
        raise SystemExit(
            "Enabled Specialist not found: "
            f"{args.specialist}"
        )

    domains = tuple(
        value.strip().casefold()
        for value in (
            args.domains
            or ""
        ).split(",")
        if value.strip()
    )

    task = SpecialistTask(
        task_id=(
            "context-preview-"
            + uuid4().hex[:12]
        ),
        investigation_id=(
            "context-preview"
        ),
        server_id=1,
        report_id=1,
        specialist_id=(
            specialist.slug
        ),
        objective=args.objective,
        knowledge_topics=(
            specialist.knowledge_topics
        ),
    )

    retriever = (
        KnowledgeHybridRetriever(
            repository=(
                KnowledgeRetrievalRepository()
            ),
            embedding_client=(
                create_embedding_client(
                    settings
                )
            ),
            hnsw_ef_search=(
                settings.rag_hnsw_ef_search
            ),
        )
    )

    builder = SpecialistContextBuilder(
        knowledge_retriever=retriever
    )

    snapshot = await builder.build(
        task=task,
        specialist=specialist,
        detected_domains=domains,
    )

    print()
    print(
        "Specialist Context Preview"
    )
    print("=" * 100)
    print(
        f"Specialist:       "
        f"{snapshot.specialist_slug}"
    )
    print(
        f"Objective:        "
        f"{snapshot.objective}"
    )
    print(
        "Domains:          "
        + (
            ", ".join(
                snapshot.domains
            )
            or "—"
        )
    )
    print(
        f"Knowledge chunks: "
        f"{len(snapshot.knowledge_chunks)}"
    )
    print(
        f"Source refs:      "
        f"{len(snapshot.knowledge_sources)}"
    )
    print(
        f"Context chars:    "
        f"{snapshot.character_count}"
    )

    print()
    print("## KNOWLEDGE QUERY")
    print(
        snapshot.knowledge_query
    )

    print()
    print("## RENDERED CONTEXT")
    print(
        snapshot.rendered_context
    )

    return 0


def main() -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "specialist"
    )
    parser.add_argument(
        "objective"
    )
    parser.add_argument(
        "--domains"
    )

    args = parser.parse_args()

    return asyncio.run(
        run(args)
    )


if __name__ == "__main__":
    raise SystemExit(main())
