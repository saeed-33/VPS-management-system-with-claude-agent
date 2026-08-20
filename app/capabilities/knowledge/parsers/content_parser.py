"""تحليل النص وHTML وPDF إلى وثيقة معرفة موحدة."""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
from app.core.contracts.knowledge_sources.parsed_document import ParsedKnowledgeDocument
from .html_text_extractor import _HTMLTextExtractor
from .text_normalization import normalize_text

class KnowledgeContentParser:
    """
    يختار محلل النص أو HTML أو PDF وينتج وثيقة معرفة موحدة.
    """
    def parse(
        self,
        *,
        content: bytes,
        canonical_uri: str,
        media_type: str | None,
        title_hint: str | None = None,
    ) -> ParsedKnowledgeDocument:
        """
        يختار استراتيجية التحليل حسب نوع الوسيط ويرفض الأنواع غير المدعومة.
        """
        normalized_media_type = (
            (media_type or "")
            .split(";", 1)[0]
            .strip()
            .casefold()
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
            or normalized_media_type in {"", "application/markdown"}
        ):
            return self._parse_text(
                content=content,
                canonical_uri=canonical_uri,
                media_type=normalized_media_type or "text/plain",
                title_hint=title_hint,
            )

        raise ValueError(
            "Unsupported knowledge media type: "
            f"{normalized_media_type or 'unknown'}"
        )

    def parse_file(
        self,
        path: Path,
        *,
        canonical_uri: str | None = None,
        title_hint: str | None = None,
    ) -> ParsedKnowledgeDocument:
        """
        يحدد نوع الوسيط من امتداد الملف ثم يقرأه ويمرره إلى المحلل الموحد.
        """
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
        """
        يفك بايتات النص بترميز UTF-8 مرن وينشئ وثيقة نصية محللة.
        """
        text = normalize_text(
            content.decode("utf-8", errors="replace")
        )

        return ParsedKnowledgeDocument(
            canonical_uri=canonical_uri,
            title=title_hint,
            media_type=media_type,
            text=text,
            parser_name="plain-text",
            parser_version="2",
        )

    def _parse_html(
        self,
        *,
        content: bytes,
        canonical_uri: str,
        media_type: str,
        title_hint: str | None,
    ) -> ParsedKnowledgeDocument:
        """
        يستخرج النص والعنوان والعناوين من HTML وينشئ وثيقة مع بياناتها الوصفية.
        """
        html = content.decode("utf-8", errors="replace")
        extractor = _HTMLTextExtractor()
        extractor.feed(html)

        return ParsedKnowledgeDocument(
            canonical_uri=canonical_uri,
            title=extractor.title or title_hint,
            media_type=media_type,
            text=extractor.text(),
            parser_name="stdlib-html-parser",
            parser_version="2",
            metadata={
                "html_headings": extractor.headings,
            },
        )

    def _parse_pdf(
        self,
        *,
        content: bytes,
        canonical_uri: str,
        title_hint: str | None,
    ) -> ParsedKnowledgeDocument:
        """
        يستخرج نص كل صفحة وبيانات PDF الوصفية وينشئ وثيقة تحمل الصفحات والعنوان.
        """
        reader = PdfReader(BytesIO(content))
        pages: list[dict] = []

        for index, page in enumerate(reader.pages, start=1):
            page_text = normalize_text(page.extract_text() or "")
            pages.append(
                {
                    "page_number": index,
                    "text": page_text,
                }
            )

        text = normalize_text(
            "\n\n".join(
                item["text"]
                for item in pages
                if item["text"]
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
            parser_version="2",
            metadata={
                "pages": pages,
                "pdf_metadata": {
                    str(key): str(value)
                    for key, value in metadata.items()
                    if value is not None
                },
            },
        )
