from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.analysis.retrieval.embedding_factory import (
    create_embedding_client,
)
from app.agent.investigation.knowledge_indexer import (
    KnowledgeIndexer,
)
from app.bootstrap import container
from app.shared.config import settings


async def run(
    *,
    document_id: int,
    force: bool,
) -> int:
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
