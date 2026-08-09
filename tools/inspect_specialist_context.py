from __future__ import annotations

import argparse
import asyncio
from uuid import uuid4
import sys
from pathlib import Path

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from app.agent.analysis.retrieval.embedding_factory import (
    create_embedding_client,
)
from app.agent.investigation.contracts import (
    SpecialistTask,
)
from app.agent.investigation.knowledge_retrieval import (
    KnowledgeHybridRetriever,
)
from app.agent.investigation.specialist_context import (
    SpecialistContextBuilder,
)
from app.bootstrap import container
from app.shared.config import settings
from app.shared.database.repositories.knowledge_retrieval_repository import (
    KnowledgeRetrievalRepository,
)


async def run(args) -> int:
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
