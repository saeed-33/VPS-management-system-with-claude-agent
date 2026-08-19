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

from .analysis_investigation_composition import AnalysisInvestigationComposition
from .retrieval_composition import RetrievalComposition


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
