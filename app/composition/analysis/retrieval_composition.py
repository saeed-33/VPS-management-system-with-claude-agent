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


@dataclass(slots=True, frozen=True)
class RetrievalComposition:
    """
    يحمل مكونات الاسترجاع المتجهي والنصي والهجين وسياسة إعادة الاستخدام وسياق RAG.
    """
    retrieval_indexer: RetrievalIndexer | None
    rag_retriever: HybridRetriever | None
    rag_context_builder: RagContextBuilder | None
    report_pdf_service: ReportPdfService | None
