from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.bootstrap import container


def main() -> int:
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
