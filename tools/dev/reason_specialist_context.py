"""
أداة تطوير/تشخيص لتشغيل workflow أو فحص contracts والبيانات أثناء التطوير.

الموقع في المعمارية: Developer tooling.
يُستدعى بواسطة: CLI أو المطور مباشرة.
يعتمد مباشرة على: app.capabilities.analysis.retrieval.embedding_factory، app.core.contracts.investigation، app.capabilities.knowledge.retrieval، app.capabilities.investigation.specialist_context، app.capabilities.investigation.specialist_reasoning_agent، app.capabilities.investigation.specialist_reasoning_client.
الحد المعماري: ليست application boundary ولا ينبغي اعتبارها API production.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.capabilities.analysis.retrieval.embedding_factory import (
    create_embedding_client,
)
from app.core.contracts.investigation import SpecialistTask
from app.capabilities.knowledge.retrieval import (
    KnowledgeHybridRetriever,
)
from app.capabilities.investigation.specialist_context import (
    SpecialistContextBuilder,
)
from app.capabilities.investigation.specialist_reasoning_agent import (
    SpecialistReasoningAgent,
)
from app.capabilities.investigation.specialist_reasoning_client import (
    create_specialist_reasoning_client,
)
from app.composition import container
from app.core.config import settings
from app.infrastructure.database.repositories.knowledge_retrieval_repository import (
    KnowledgeRetrievalRepository,
)


async def run(args) -> int:
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى run؛ المدخلات المهمة: args.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
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
    """
    يشغّل workflow الخاص بالأداة ويحدد exit/result النهائي ضمن طبقة Developer tooling.

    تُستدعى عندما يصل المسار إلى main؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد int أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. قد يعيد exit code أو يرفع exception عند فشل المدخلات أو dependency.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("specialist")
    parser.add_argument("objective")
    parser.add_argument("--domains")
    args = parser.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
