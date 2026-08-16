"""
جزء من Retrieval/RAG لتطبيع report أو استرجاع context أو الفهرسة.

الموقع في المعمارية: Application capability / retrieval.
يُستدعى بواسطة: Analysis orchestrator وخدمات الفهرسة.
يعتمد مباشرة على: app.capabilities.analysis.retrieval.embedding_client، app.infrastructure.database.repositories.analysis_repository، app.infrastructure.database.repositories.retrieval_repository.
الحد المعماري: ينتهي عند context مع provenance؛ reasoning مسؤولية أعلى.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
import json
import logging

from app.capabilities.analysis.retrieval.embedding_client import EmbeddingClient
from app.infrastructure.database.repositories.analysis_repository import AnalysisRepository
from app.infrastructure.database.repositories.retrieval_repository import RetrievalRepository

logger = logging.getLogger(__name__)


class RetrievalIndexer:
    """
    يمثل RetrievalIndexer مسؤولية محددة داخل طبقة Application capability / retrieval.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه Analysis orchestrator وخدمات الفهرسة
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(self, *, analysis_repository: AnalysisRepository, retrieval_repository: RetrievalRepository, embedding_client: EmbeddingClient) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: analysis_repository، retrieval_repository، embedding_client.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ خطوة من Retrieval أو Knowledge pipeline وينقل provenance ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى index_reused_analysis؛ المدخلات المهمة: source_analysis_id، target_analysis_id.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ خطوة من Retrieval أو Knowledge pipeline وينقل provenance ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى index_analysis؛ المدخلات المهمة: analysis_id.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / retrieval.

        تُستدعى عندما يصل workflow إلى _collect_error_signatures؛ المدخلات المهمة: payload.
        تعيد list[str] أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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

