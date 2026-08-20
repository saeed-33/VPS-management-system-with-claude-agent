"""
فهرسة التحليلات المكتملة في مخزن الاسترجاع.

ينشئ embedding والميزات المنظمة وتوقيعات الأخطاء، أو ينسخ مستند استرجاع سابق
عند إعادة استخدام تحليل، مع تسجيل مسار النسخ أو إعادة التوليد.
"""
import json
import logging

from app.core.ports.analysis.embedding_client import EmbeddingClient
from app.core.ports.analysis.analysis_repository import AnalysisRepositoryPort
from app.core.ports.analysis.retrieval_repository import AnalysisRetrievalRepositoryPort

logger = logging.getLogger(__name__)


class RetrievalIndexer:
    """
    يدير إنشاء مستندات الاسترجاع للتحليلات المكتملة أو نسخ مستند التحليل المعاد استخدامه.
    """
    def __init__(self, *, analysis_repository: AnalysisRepositoryPort, retrieval_repository: AnalysisRetrievalRepositoryPort, embedding_client: EmbeddingClient) -> None:
        """
        يربط مستودعي التحليل والاسترجاع وعميل embedding اللازم لبناء المستندات.
        """
        self._analysis_repository = analysis_repository
        self._retrieval_repository = retrieval_repository
        self._embedding_client = embedding_client

    async def index_reused_analysis(
        self,
        *,
        source_analysis_id: int,
        target_analysis_id: int,
    ) -> str:
        """
        يحاول نسخ مستند الاسترجاع من التحليل المصدر، ويعيد فهرسته عند تعذر النسخ.
        """
        target_analysis = self._analysis_repository.get_by_id(
            target_analysis_id
        )

        if target_analysis is None:
            raise ValueError(
                f"Analysis {target_analysis_id} was not found."
            )

        cloned = self._retrieval_repository.clone_document(
            source_analysis_id=source_analysis_id,
            target_analysis_id=target_analysis_id,
            target_report_id=target_analysis.report_id,
            target_server_id=target_analysis.server_id,
            target_fingerprint=target_analysis.report_fingerprint,
            target_normalized_text=target_analysis.normalized_report,
            target_health_status=target_analysis.health_status,
        )

        if cloned is not None:
            logger.info(
                "Analysis retrieval document cloned | "
                "source_analysis_id=%s | target_analysis_id=%s",
                source_analysis_id,
                target_analysis_id,
            )
            return "cloned"

        await self.index_analysis(target_analysis_id)

        logger.warning(
            "Source retrieval document unavailable; "
            "embedding regenerated | "
            "source_analysis_id=%s | target_analysis_id=%s",
            source_analysis_id,
            target_analysis_id,
        )
        return "embedded_fallback"

    async def index_analysis(self, analysis_id: int) -> None:
        """
        يتحقق من اكتمال التحليل، ينتج embedding وميزات منظمة، ثم يحدّث مستند الاسترجاع.
        """
        analysis = self._analysis_repository.get_by_id(analysis_id)
        if analysis is None:
            raise ValueError(f"Analysis {analysis_id} was not found.")
        if analysis.status != "completed":
            raise ValueError(f"Analysis {analysis_id} is not completed.")
        if not analysis.report_fingerprint or not analysis.normalized_report:
            raise ValueError(f"Analysis {analysis_id} has no retrieval metadata.")

        embedding = await self._embedding_client.embed(analysis.normalized_report)
        normalized_payload = json.loads(
            analysis.normalized_report
        )
        executions = normalized_payload.get("executions", [])
        failed_command_ids = sorted(
            {
                execution["command_id"]
                for execution in executions
                if not execution.get("success", False)
                and execution.get("command_id") is not None
            }
        )
        error_signatures = self._collect_error_signatures(
            normalized_payload
        )
        features = {
            "health_status": analysis.health_status,
            "analysis_source": analysis.analysis_source,
            "llm_called": analysis.llm_called,
            "monitoring_profile_id": normalized_payload.get(
                "monitoring_profile_id"
            ),
            "command_set_hash": normalized_payload.get(
                "command_set_hash"
            ),
            "connection_successful": normalized_payload.get(
                "connection_successful"
            ),
            "failed_command_ids": failed_command_ids,
            "error_signatures": error_signatures,
        }
        self._retrieval_repository.upsert_document(
            report_id=analysis.report_id, analysis_id=analysis.id, server_id=analysis.server_id,
            monitoring_profile_id=normalized_payload.get(
                "monitoring_profile_id"
            ),
            command_set_hash=normalized_payload.get(
                "command_set_hash"
            ),
            connection_successful=normalized_payload.get(
                "connection_successful"
            ),
            failed_command_ids=failed_command_ids,
            error_signatures=error_signatures,
            fingerprint=analysis.report_fingerprint, normalized_text=analysis.normalized_report,
            structured_features=features, embedding=embedding,
            embedding_provider=self._embedding_client.provider_name,
            embedding_model=self._embedding_client.model_name,
            embedding_dimensions=self._embedding_client.dimensions,
            analysis_health_status=analysis.health_status,
        )
        logger.info("Analysis retrieval document indexed | analysis_id=%s", analysis_id)

    @staticmethod
    def _collect_error_signatures(
        payload: dict,
    ) -> list[str]:
        """
        يجمع رسائل الأخطاء ومخرجات stderr الفريدة والمحدودة من التقرير المطبع.
        """
        signatures: set[str] = set()

        report_error = payload.get("error_message")
        if report_error:
            signatures.add(str(report_error)[:500])

        for execution in payload.get("executions", []):
            for field in ("error_message", "stderr"):
                value = execution.get(field)
                if value:
                    signatures.add(str(value)[:500])

        return sorted(signatures)
