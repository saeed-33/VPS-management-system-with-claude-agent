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
from app.capabilities.analysis.analysis_orchestrator.orchestrator import AnalysisOrchestrator
from app.capabilities.analysis.client_factory import create_llm_analysis_client
from app.capabilities.analysis.report_analyzer import ReportAnalyzer
from app.capabilities.analysis.retrieval.context_builder import RagContextBuilder
from app.capabilities.analysis.retrieval.embedding_factory import create_embedding_client
from app.capabilities.analysis.retrieval.full_text_retriever.retriever import FullTextRetriever
from app.capabilities.analysis.retrieval.hybrid_retriever.retriever import HybridRetriever
from app.capabilities.analysis.retrieval.rag_retriever import RagRetriever
from app.capabilities.analysis.retrieval.retrieval_indexer import RetrievalIndexer
from app.capabilities.analysis.retrieval.structured_compatibility.checker import StructuredCompatibilityChecker
from app.capabilities.investigation.specialist_context.specialist_context_builder import SpecialistContextBuilder
from app.capabilities.investigation.specialist_investigation_loop.specialist_investigation_loop import SpecialistInvestigationLoop
from app.capabilities.investigation.specialist_reasoning_agent.specialist_reasoning_agent import SpecialistReasoningAgent
from app.capabilities.investigation.specialist_reasoning_client import (
    create_specialist_reasoning_client,
)
from app.capabilities.knowledge.retrieval.retriever import KnowledgeHybridRetriever
from app.core.config import Settings
from app.infrastructure.database.repositories.knowledge_retrieval_repository.repository import KnowledgeRetrievalRepository


logger = logging.getLogger(__name__)

from .retrieval_composition import RetrievalComposition


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
