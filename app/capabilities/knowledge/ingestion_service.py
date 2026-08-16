"""
جزء من Knowledge ingestion/indexing/retrieval لتغذية RAG بمصادر قابلة للتتبع.

الموقع في المعمارية: Application capability / knowledge.
يُستدعى بواسطة: أدوات الإدارة أو Retrieval.
يعتمد مباشرة على: app.capabilities.knowledge.parsers، app.capabilities.knowledge.source_loader، app.infrastructure.database.repositories.knowledge_document_repository، app.infrastructure.database.repositories.knowledge_source_repository، app.core.utils.datetime.
الحد المعماري: لا يخلط knowledge retrieval مع reasoning.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from hashlib import sha256

from app.capabilities.knowledge.parsers import (
    KnowledgeContentParser,
)
from app.capabilities.knowledge.source_loader import (
    KnowledgeSourceLoader,
)
from app.infrastructure.database.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from app.infrastructure.database.repositories.knowledge_source_repository import (
    KnowledgeSourceRepository,
)
from app.core.utils.datetime import utc_now


class KnowledgeIngestionService:
    """
    يمثل KnowledgeIngestionService مسؤولية محددة داخل طبقة Application capability / knowledge.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه أدوات الإدارة أو Retrieval
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    def __init__(
        self,
        *,
        source_repository: KnowledgeSourceRepository,
        document_repository: KnowledgeDocumentRepository,
        loader: KnowledgeSourceLoader,
        parser: KnowledgeContentParser,
    ) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: source_repository، document_repository، loader، parser.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        self._source_repository = source_repository
        self._document_repository = document_repository
        self._loader = loader
        self._parser = parser

    def ingest_source(
        self,
        source_id: int,
    ):
        """
        ينفذ خطوة من Retrieval أو Knowledge pipeline وينقل provenance ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى ingest_source؛ المدخلات المهمة: source_id.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        source = self._source_repository.get_by_id(
            source_id
        )

        if source is None:
            raise LookupError(
                "Knowledge source not found."
            )

        if not source.enabled:
            raise ValueError(
                "Knowledge source is disabled."
            )

        fallback_uri = (
            str(source.source_uri or "").strip()
            or f"inline://knowledge-source/{source.slug}"
        )

        try:
            loaded = self._loader.load(source)
            fetched_at = utc_now()

            parsed = self._parser.parse(
                content=loaded.content,
                canonical_uri=loaded.canonical_uri,
                media_type=loaded.media_type,
                title_hint=loaded.title_hint,
            )

            content_hash = sha256(
                parsed.text.encode("utf-8")
            ).hexdigest()

            return self._document_repository.upsert_parsed(
                source_id=source.id,
                parsed=parsed,
                content_hash=content_hash,
                fetched_at=fetched_at,
            )

        except Exception as exc:
            self._document_repository.mark_failed(
                source_id=source.id,
                canonical_uri=fallback_uri,
                error_message=f"{type(exc).__name__}: {exc}",
            )
            raise
