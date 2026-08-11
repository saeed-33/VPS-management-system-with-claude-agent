import pytest
from app.domain.knowledge.ingestion_contracts import (
    KnowledgeChunkDraft, KnowledgeDocumentStatus, ParsedKnowledgeDocument,
)

def test_document_status_lifecycle_is_explicit():
    assert [x.value for x in KnowledgeDocumentStatus] == [
        "pending", "fetched", "parsed", "chunked", "indexed", "failed"
    ]

def test_parsed_document_requires_text():
    with pytest.raises(ValueError, match="text must not be empty"):
        ParsedKnowledgeDocument(
            canonical_uri="https://example.com/doc",
            title="Example", media_type="text/html", text="   "
        )

def test_parsed_document_accepts_large_document_metadata():
    item = ParsedKnowledgeDocument(
        canonical_uri="file:///manual.pdf",
        title="Large Manual", media_type="application/pdf",
        text="Useful content", page_count=100, parser_name="pdf-parser"
    )
    assert item.page_count == 100

def test_chunk_draft_preserves_page_and_section():
    chunk = KnowledgeChunkDraft(
        chunk_index=7, section_title="CPU Scheduling",
        page_number=52, content="Scheduler diagnostic guidance.",
        token_count=12
    )
    assert chunk.page_number == 52
    assert chunk.section_title == "CPU Scheduling"

def test_chunk_index_is_zero_based():
    KnowledgeChunkDraft(chunk_index=0, content="First chunk")
    with pytest.raises(ValueError, match="chunk_index must be >= 0"):
        KnowledgeChunkDraft(chunk_index=-1, content="Invalid")
