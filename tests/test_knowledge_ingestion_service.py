from types import SimpleNamespace

from app.domain.knowledge.ingestion_service import (
    KnowledgeIngestionService,
)
from app.domain.knowledge.parsers import (
    KnowledgeContentParser,
)
from app.domain.knowledge.source_loader import (
    LoadedKnowledgeContent,
)


class SourceRepository:
    def __init__(self, source):
        self.source = source

    def get_by_id(self, source_id):
        if source_id == self.source.id:
            return self.source
        return None


class Loader:
    def load(self, source):
        return LoadedKnowledgeContent(
            content=b"Diagnostic runbook content.",
            canonical_uri="inline://knowledge-source/runbook",
            media_type="text/plain",
            title_hint="Runbook",
        )


class DocumentRepository:
    def __init__(self):
        self.saved = None
        self.failed = None

    def upsert_parsed(self, **kwargs):
        self.saved = kwargs
        return SimpleNamespace(
            id=7,
            status="parsed",
            **kwargs,
        )

    def mark_failed(self, **kwargs):
        self.failed = kwargs


def test_ingestion_persists_parsed_document():
    source = SimpleNamespace(
        id=3,
        enabled=True,
        source_uri=None,
        slug="runbook",
    )
    documents = DocumentRepository()

    service = KnowledgeIngestionService(
        source_repository=SourceRepository(source),
        document_repository=documents,
        loader=Loader(),
        parser=KnowledgeContentParser(),
    )

    result = service.ingest_source(3)

    assert result.status == "parsed"
    assert documents.saved["source_id"] == 3
    assert documents.saved["parsed"].text == "Diagnostic runbook content."
    assert len(documents.saved["content_hash"]) == 64
