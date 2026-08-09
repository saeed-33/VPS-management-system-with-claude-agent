from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent.analysis.retrieval.embedding_factory import (
    create_embedding_client,
)
from app.agent.investigation.contracts import SpecialistTask
from app.agent.investigation.knowledge_retrieval import (
    KnowledgeHybridRetriever,
)
from app.agent.investigation.specialist_context import (
    SpecialistContextBuilder,
)
from app.agent.investigation.specialist_reasoning_agent import (
    SpecialistReasoningAgent,
)
from app.agent.investigation.specialist_reasoning_client import (
    create_specialist_reasoning_client,
)
from app.bootstrap import container
from app.shared.config import settings
from app.shared.database.repositories.knowledge_retrieval_repository import (
    KnowledgeRetrievalRepository,
)


async def run(args) -> int:
    specialist = container.specialist_registry.get_by_slug(
        args.specialist
    )

    if specialist is None:
        raise SystemExit(
            f"Enabled Specialist not found: {args.specialist}"
        )

    domains = tuple(
        value.strip().casefold()
        for value in (args.domains or "").split(",")
        if value.strip()
    )

    task = SpecialistTask(
        task_id="reason-preview-" + uuid4().hex[:12],
        investigation_id="reason-preview",
        server_id=1,
        report_id=1,
        specialist_id=specialist.slug,
        objective=args.objective,
        knowledge_topics=specialist.knowledge_topics,
    )

    retriever = KnowledgeHybridRetriever(
        repository=KnowledgeRetrievalRepository(),
        embedding_client=create_embedding_client(settings),
        hnsw_ef_search=settings.rag_hnsw_ef_search,
    )

    context = await SpecialistContextBuilder(
        knowledge_retriever=retriever
    ).build(
        task=task,
        specialist=specialist,
        detected_domains=domains,
    )

    enabled_slugs = tuple(
        item.slug
        for item in container.specialist_registry.get_enabled()
    )

    execution = await SpecialistReasoningAgent(
        client=create_specialist_reasoning_client(settings)
    ).reason(
        context=context,
        allowed_specialist_slugs=enabled_slugs,
    )

    result = execution.result

    print()
    print("Specialist Reasoning Result")
    print("=" * 100)
    print(f"Specialist:       {result.specialist_id}")
    print(f"Provider/model:   {execution.provider}/{execution.model}")
    print(f"Status:           {result.status.value}")
    print(f"Confidence:       {result.confidence:.2f}")
    print(f"Findings:         {len(result.findings)}")
    print(f"Hypotheses:       {len(result.hypotheses)}")
    print(f"Missing evidence: {len(result.missing_evidence)}")
    print()
    print("## SUMMARY")
    print(result.summary)

    if result.findings:
        print()
        print("## FINDINGS")
        for item in result.findings:
            print(
                f"- {item.finding_id} | confidence={item.confidence:.2f}"
            )
            print(f"  {item.title}: {item.description}")
            print(
                "  evidence="
                + (", ".join(item.evidence_ids) or "—")
            )
            print(
                "  knowledge="
                + (", ".join(item.knowledge_source_ids) or "—")
            )

    if result.hypotheses:
        print()
        print("## HYPOTHESES")
        for item in result.hypotheses:
            print(
                f"- {item.hypothesis_id} | "
                f"confidence={item.confidence:.2f} | "
                f"{item.statement}"
            )

    if result.missing_evidence:
        print()
        print("## MISSING EVIDENCE")
        for item in result.missing_evidence:
            print(f"- {item}")

    if result.recommended_next_specialists:
        print()
        print("## RECOMMENDED NEXT SPECIALISTS")
        for item in result.recommended_next_specialists:
            print(f"- {item}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("specialist")
    parser.add_argument("objective")
    parser.add_argument("--domains")
    args = parser.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
