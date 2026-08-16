"""
تركيب مكونات التحليل والاسترجاع والتحقيق.

يبني هذا الملف حزم الاعتماديات التي تحتاجها مراحل التحليل والتحقيق، ويربط
المستودعات والعملاء والسياسات دون تنفيذ دورة العمل بنفسه.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from app.interfaces.admin.services.report_pdf_service import ReportPdfService
from app.composition.repositories import RepositoryBundle
from app.composition.services import CoreServiceBundle
from app.capabilities.analysis.analysis_orchestrator import AnalysisOrchestrator
from app.capabilities.analysis.client_factory import create_llm_analysis_client
from app.capabilities.analysis.report_analyzer import ReportAnalyzer
from app.capabilities.analysis.retrieval.context_builder import RagContextBuilder
from app.capabilities.analysis.retrieval.embedding_factory import create_embedding_client
from app.capabilities.analysis.retrieval.full_text_retriever import FullTextRetriever
from app.capabilities.analysis.retrieval.hybrid_retriever import HybridRetriever
from app.capabilities.analysis.retrieval.rag_retriever import RagRetriever
from app.capabilities.analysis.retrieval.retrieval_indexer import RetrievalIndexer
from app.capabilities.analysis.retrieval.structured_compatibility import (
    StructuredCompatibilityChecker,
)
from app.capabilities.investigation.specialist_context import SpecialistContextBuilder
from app.capabilities.investigation.specialist_investigation_loop import (
    SpecialistInvestigationLoop,
)
from app.capabilities.investigation.specialist_reasoning_agent import (
    SpecialistReasoningAgent,
)
from app.capabilities.investigation.specialist_reasoning_client import (
    create_specialist_reasoning_client,
)
from app.capabilities.knowledge.retrieval import KnowledgeHybridRetriever
from app.core.config import Settings
from app.infrastructure.database.repositories.knowledge_retrieval_repository import (
    KnowledgeRetrievalRepository,
)


logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class RetrievalComposition:
    """
    يحمل مكونات الاسترجاع المتجهي والنصي والهجين وسياسة إعادة الاستخدام وسياق RAG.
    """
    retrieval_indexer: RetrievalIndexer | None
    rag_retriever: HybridRetriever | None
    rag_context_builder: RagContextBuilder | None
    report_pdf_service: ReportPdfService | None


@dataclass(slots=True, frozen=True)
class AnalysisInvestigationComposition:
    """
    يحمل مكونات التحليل والتحقيق ومخازن المصادر والخدمات المرتبطة بهما.
    """
    specialist_knowledge_retriever: KnowledgeHybridRetriever | None
    specialist_investigation_loop: SpecialistInvestigationLoop | None
    report_analyzer: ReportAnalyzer | None
    analysis_orchestrator: AnalysisOrchestrator | None


def build_retrieval_composition(
    repositories: RepositoryBundle,
    settings: Settings,
) -> RetrievalComposition:
    """
    ينشئ عملاء embedding ومستودعات الاسترجاع وبناة السياق ومشغلي البحث وفق الإعدادات.
    """
    embedding_client = None
    retrieval_indexer = None
    vector_retriever = None
    full_text_retriever = None
    compatibility_checker = None
    rag_retriever = None
    rag_context_builder = None
    report_pdf_service = None

    try:
        report_pdf_service = ReportPdfService(
            font_path=settings.pdf_font_path,
        )
    except FileNotFoundError:
        logger.exception(
            "PDF service disabled because font was not found."
        )

    if settings.rag_vector_enabled:
        embedding_client = create_embedding_client(
            settings
        )
        retrieval_indexer = RetrievalIndexer(
            analysis_repository=repositories.analysis_repository,
            retrieval_repository=repositories.retrieval_repository,
            embedding_client=embedding_client,
        )
        vector_retriever = RagRetriever(
            embedding_client=embedding_client,
            retrieval_repository=repositories.retrieval_repository,
            analysis_repository=repositories.analysis_repository,
            top_k=settings.rag_top_k,
            minimum_score=settings.rag_minimum_similarity,
            hnsw_ef_search=settings.rag_hnsw_ef_search,
        )

    if settings.rag_full_text_enabled:
        full_text_retriever = FullTextRetriever(
            retrieval_repository=repositories.retrieval_repository,
            candidate_limit=settings.rag_full_text_candidate_limit,
            minimum_rank=settings.rag_full_text_minimum_rank,
        )

    if (
        settings.rag_assisted_enabled
        and (
            vector_retriever is not None
            or full_text_retriever is not None
        )
    ):
        if settings.rag_structured_compatibility_enabled:
            compatibility_checker = StructuredCompatibilityChecker()

        rag_retriever = HybridRetriever(
            analysis_repository=repositories.analysis_repository,
            retrieval_repository=repositories.retrieval_repository,
            compatibility_checker=compatibility_checker,
            vector_retriever=vector_retriever,
            full_text_retriever=full_text_retriever,
            top_k=settings.rag_context_top_k,
            rrf_k=settings.rag_rrf_k,
            minimum_vector_score=settings.rag_minimum_similarity,
        )
        rag_context_builder = RagContextBuilder()

    return RetrievalComposition(
        retrieval_indexer=retrieval_indexer,
        rag_retriever=rag_retriever,
        rag_context_builder=rag_context_builder,
        report_pdf_service=report_pdf_service,
    )


def build_analysis_investigation_composition(
    repositories: RepositoryBundle,
    services: CoreServiceBundle,
    retrieval: RetrievalComposition,
    settings: Settings,
) -> AnalysisInvestigationComposition:
    """
    يربط محلل التقارير والمنسق وخدمات التحقيق مع حزمة المستودعات والخدمات الأساسية.
    """
    specialist_knowledge_retriever = None
    specialist_investigation_loop = None
    report_analyzer = None
    analysis_orchestrator = None

    if settings.llm_enabled:
        llm_client = create_llm_analysis_client(
            settings
        )

        specialist_knowledge_retriever = KnowledgeHybridRetriever(
            repository=KnowledgeRetrievalRepository(),
            embedding_client=create_embedding_client(
                settings
            ),
            hnsw_ef_search=settings.rag_hnsw_ef_search,
        )

        specialist_context_builder = SpecialistContextBuilder(
            knowledge_retriever=specialist_knowledge_retriever
        )

        specialist_reasoning_agent = SpecialistReasoningAgent(
            client=create_specialist_reasoning_client(
                settings
            )
        )

        specialist_investigation_loop = SpecialistInvestigationLoop(
            context_builder=specialist_context_builder,
            reasoning_agent=specialist_reasoning_agent,
            diagnostic_tool_registry=services.diagnostic_tool_registry,
            diagnostic_policy_engine=services.diagnostic_policy_engine,
            evidence_collection_service=services.evidence_collection_service,
        )

        report_analyzer = ReportAnalyzer(
            report_query_service=services.report_query_service,
            analysis_repository=repositories.analysis_repository,
            llm_client=llm_client,
            max_report_characters=settings.llm_max_report_characters,
        )

        analysis_orchestrator = AnalysisOrchestrator(
            report_query_service=services.report_query_service,
            analysis_repository=repositories.analysis_repository,
            report_analyzer=report_analyzer,
            exact_reuse_enabled=settings.rag_exact_reuse_enabled,
            retrieval_indexer=retrieval.retrieval_indexer,
            rag_retriever=retrieval.rag_retriever,
            rag_context_builder=retrieval.rag_context_builder,
            analysis_source_repository=repositories.analysis_source_repository,
            rag_assisted_enabled=settings.rag_assisted_enabled,
        )

    return AnalysisInvestigationComposition(
        specialist_knowledge_retriever=specialist_knowledge_retriever,
        specialist_investigation_loop=specialist_investigation_loop,
        report_analyzer=report_analyzer,
        analysis_orchestrator=analysis_orchestrator,
    )


__all__ = [
    "AnalysisInvestigationComposition",
    "RetrievalComposition",
    "build_analysis_investigation_composition",
    "build_retrieval_composition",
]
