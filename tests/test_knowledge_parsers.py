from app.capabilities.knowledge.parsers import (
    KnowledgeContentParser,
    normalize_text,
)


def test_normalize_text_collapses_spacing():
    assert normalize_text(
        "  Alpha   beta\n\n\n Gamma "
    ) == "Alpha beta\n\nGamma"


def test_html_parser_removes_script_and_extracts_title():
    parser = KnowledgeContentParser()

    result = parser.parse(
        content=b"""
        <html>
          <head>
            <title>CPU Guide</title>
            <script>ignore_me()</script>
          </head>
          <body>
            <h1>CPU Scheduling</h1>
            <p>Check the run queue.</p>
          </body>
        </html>
        """,
        canonical_uri="https://example.com/cpu",
        media_type="text/html",
    )

    assert result.title == "CPU Guide"
    assert "CPU Scheduling" in result.text
    assert "Check the run queue." in result.text
    assert "ignore_me" not in result.text


def test_plain_text_parser():
    parser = KnowledgeContentParser()

    result = parser.parse(
        content=b"CPU usage is normal.",
        canonical_uri="inline://example",
        media_type="text/plain",
        title_hint="Example",
    )

    assert result.text == "CPU usage is normal."
    assert result.parser_name == "plain-text"
