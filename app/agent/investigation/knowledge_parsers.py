from __future__ import annotations

from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
import re

from pypdf import PdfReader

from app.agent.investigation.knowledge_ingestion_contracts import (
    ParsedKnowledgeDocument,
)


_SPACE_RE = re.compile(r"[ \t]+")
_BLANKS_RE = re.compile(r"\n{3,}")


def normalize_text(value: str) -> str:
    lines = [
        _SPACE_RE.sub(" ", line).strip()
        for line in value.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    ]
    return _BLANKS_RE.sub(
        "\n\n",
        "\n".join(lines),
    ).strip()


class _HTMLTextExtractor(HTMLParser):
    BLOCK_TAGS = {
        "article", "aside", "blockquote", "br", "div", "footer",
        "h1", "h2", "h3", "h4", "h5", "h6", "header",
        "li", "main", "nav", "p", "pre", "section", "table",
        "td", "th", "tr",
    }

    SKIP_TAGS = {
        "script", "style", "noscript", "svg",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0
        self.title: str | None = None
        self._in_title = False
        self._title_parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.casefold()

        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
            return

        if self._skip_depth:
            return

        if tag == "title":
            self._in_title = True

        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag):
        tag = tag.casefold()

        if tag in self.SKIP_TAGS:
            if self._skip_depth:
                self._skip_depth -= 1
            return

        if self._skip_depth:
            return

        if tag == "title":
            self._in_title = False
            value = normalize_text(" ".join(self._title_parts))
            self.title = value or None

        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data):
        if self._skip_depth:
            return

        value = data.strip()

        if not value:
            return

        if self._in_title:
            self._title_parts.append(value)

        self._parts.append(value)
        self._parts.append(" ")

    def text(self) -> str:
        return normalize_text("".join(self._parts))


class KnowledgeContentParser:
    def parse(
        self,
        *,
        content: bytes,
        canonical_uri: str,
        media_type: str | None,
        title_hint: str | None = None,
    ) -> ParsedKnowledgeDocument:
        normalized_media_type = (
            (media_type or "").split(";", 1)[0].strip().casefold()
        )

        if normalized_media_type == "application/pdf":
            return self._parse_pdf(
                content=content,
                canonical_uri=canonical_uri,
                title_hint=title_hint,
            )

        if normalized_media_type in {
            "text/html",
            "application/xhtml+xml",
        }:
            return self._parse_html(
                content=content,
                canonical_uri=canonical_uri,
                media_type=normalized_media_type,
                title_hint=title_hint,
            )

        if (
            normalized_media_type.startswith("text/")
            or normalized_media_type in {
                "",
                "application/markdown",
            }
        ):
            return self._parse_text(
                content=content,
                canonical_uri=canonical_uri,
                media_type=normalized_media_type or "text/plain",
                title_hint=title_hint,
            )

        raise ValueError(
            f"Unsupported knowledge media type: {normalized_media_type or 'unknown'}"
        )

    def parse_file(
        self,
        path: Path,
        *,
        canonical_uri: str | None = None,
        title_hint: str | None = None,
    ) -> ParsedKnowledgeDocument:
        suffix = path.suffix.casefold()

        media_types = {
            ".pdf": "application/pdf",
            ".html": "text/html",
            ".htm": "text/html",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".markdown": "text/markdown",
        }

        media_type = media_types.get(suffix)

        if media_type is None:
            raise ValueError(
                f"Unsupported knowledge file extension: {suffix or '<none>'}"
            )

        return self.parse(
            content=path.read_bytes(),
            canonical_uri=canonical_uri or path.resolve().as_uri(),
            media_type=media_type,
            title_hint=title_hint or path.name,
        )

    def _parse_text(
        self,
        *,
        content: bytes,
        canonical_uri: str,
        media_type: str,
        title_hint: str | None,
    ) -> ParsedKnowledgeDocument:
        text = normalize_text(
            content.decode("utf-8", errors="replace")
        )

        return ParsedKnowledgeDocument(
            canonical_uri=canonical_uri,
            title=title_hint,
            media_type=media_type,
            text=text,
            parser_name="plain-text",
            parser_version="1",
        )

    def _parse_html(
        self,
        *,
        content: bytes,
        canonical_uri: str,
        media_type: str,
        title_hint: str | None,
    ) -> ParsedKnowledgeDocument:
        html = content.decode(
            "utf-8",
            errors="replace",
        )

        extractor = _HTMLTextExtractor()
        extractor.feed(html)
        text = extractor.text()

        return ParsedKnowledgeDocument(
            canonical_uri=canonical_uri,
            title=extractor.title or title_hint,
            media_type=media_type,
            text=text,
            parser_name="stdlib-html-parser",
            parser_version="1",
        )

    def _parse_pdf(
        self,
        *,
        content: bytes,
        canonical_uri: str,
        title_hint: str | None,
    ) -> ParsedKnowledgeDocument:
        reader = PdfReader(BytesIO(content))

        pages: list[str] = []

        for page in reader.pages:
            pages.append(
                normalize_text(
                    page.extract_text() or ""
                )
            )

        text = normalize_text(
            "\n\n".join(
                page
                for page in pages
                if page
            )
        )

        metadata = reader.metadata or {}
        pdf_title = (
            str(metadata.get("/Title")).strip()
            if metadata.get("/Title")
            else None
        )

        return ParsedKnowledgeDocument(
            canonical_uri=canonical_uri,
            title=pdf_title or title_hint,
            media_type="application/pdf",
            text=text,
            page_count=len(reader.pages),
            parser_name="pypdf",
            parser_version="1",
            metadata={
                "pdf_metadata": {
                    str(key): str(value)
                    for key, value in metadata.items()
                    if value is not None
                }
            },
        )
