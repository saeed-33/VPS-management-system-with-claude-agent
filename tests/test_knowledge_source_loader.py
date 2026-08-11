from types import SimpleNamespace

import pytest

from app.domain.knowledge.source_loader import (
    KnowledgeSourceLoader,
)


def test_inline_loader():
    loader = KnowledgeSourceLoader()

    result = loader.load(
        SimpleNamespace(
            source_type="inline",
            inline_content="Internal runbook",
            slug="runbook",
            name="Runbook",
            source_uri=None,
        )
    )

    assert result.content == b"Internal runbook"
    assert result.canonical_uri == "inline://knowledge-source/runbook"


def test_loader_rejects_unknown_source_type():
    loader = KnowledgeSourceLoader()

    with pytest.raises(
        ValueError,
        match="Unsupported knowledge source type",
    ):
        loader.load(
            SimpleNamespace(
                source_type="database",
            )
        )
