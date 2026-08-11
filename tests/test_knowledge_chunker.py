from app.domain.knowledge.chunker import (
    KnowledgeChunkerConfig,
    StructureAwareKnowledgeChunker,
)


def make_chunker():
    return StructureAwareKnowledgeChunker(
        KnowledgeChunkerConfig(
            target_chars=300,
            max_chars=450,
            overlap_chars=60,
            min_chars=50,
        )
    )


def test_markdown_heading_is_preserved_as_section():
    chunks = make_chunker().chunk_document(
        text=(
            "# CPU Scheduling\n\n"
            + "Run queue diagnostics. " * 20
        )
    )

    assert chunks
    assert chunks[0].section_title == "CPU Scheduling"


def test_html_heading_metadata_is_used():
    chunks = make_chunker().chunk_document(
        text=(
            "Overview\n\n"
            "General introduction.\n\n"
            "CPU Tuning\n\n"
            + "CPU details. " * 20
        ),
        metadata={
            "html_headings": ["Overview", "CPU Tuning"],
        },
    )

    assert any(
        chunk.section_title == "CPU Tuning"
        for chunk in chunks
    )


def test_pdf_page_metadata_preserves_page_number():
    chunks = make_chunker().chunk_document(
        text="fallback",
        metadata={
            "pages": [
                {
                    "page_number": 52,
                    "text": "CPU scheduling details. " * 12,
                },
            ],
        },
    )

    assert chunks
    assert all(chunk.page_number == 52 for chunk in chunks)


def test_large_document_is_split_under_max_chars():
    text = "\n\n".join(
        f"Paragraph {index}. "
        + ("Diagnostic detail. " * 12)
        for index in range(20)
    )

    chunks = make_chunker().chunk_document(text=text)

    assert len(chunks) > 1
    assert all(len(chunk.content) <= 450 for chunk in chunks)


def test_chunk_indexes_are_contiguous():
    chunks = make_chunker().chunk_document(
        text="\n\n".join(
            ("Diagnostic information. " * 12)
            for _ in range(8)
        )
    )

    assert [
        chunk.chunk_index
        for chunk in chunks
    ] == list(range(len(chunks)))
