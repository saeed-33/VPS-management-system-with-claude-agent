"""
جزء من Knowledge ingestion/indexing/retrieval لتغذية RAG بمصادر قابلة للتتبع.

الموقع في المعمارية: Application capability / knowledge.
يُستدعى بواسطة: أدوات الإدارة أو Retrieval.
يعتمد مباشرة على: app.capabilities.knowledge.ingestion_contracts.
الحد المعماري: لا يخلط knowledge retrieval مع reasoning.
سير البيانات المختصر: يستقبل contracts أو مدخلات الواجهة، ينفذ الجزء المنوط
به، ثم يعيد DTO/نتيجة أو أثرًا محفوظًا إلى caller.
"""
from __future__ import annotations

from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
import re

from pypdf import PdfReader

from app.capabilities.knowledge.ingestion_contracts import (
    ParsedKnowledgeDocument,
)


_SPACE_RE = re.compile(r"[ \t]+")
_BLANKS_RE = re.compile(r"\n{3,}")


def normalize_text(value: str) -> str:
    """
    يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة Application capability / knowledge.

    تُستدعى عندما يصل workflow إلى normalize_text؛ المدخلات المهمة: value.
    تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
    قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
    """
    lines = [
        _SPACE_RE.sub(" ", line).strip()
        for line in (
            value
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            .split("\n")
        )
    ]

    return _BLANKS_RE.sub(
        "\n\n",
        "\n".join(lines),
    ).strip()


class _HTMLTextExtractor(HTMLParser):
    """
    يمثل _HTMLTextExtractor مسؤولية محددة داخل طبقة Application capability / knowledge.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه أدوات الإدارة أو Retrieval
    ويعتمد على HTMLParser وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
    """
    BLOCK_TAGS = {
        "article", "aside", "blockquote", "br", "div",
        "footer", "h1", "h2", "h3", "h4", "h5", "h6",
        "header", "li", "main", "nav", "p", "pre",
        "section", "table", "td", "th", "tr",
    }
    HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
    SKIP_TAGS = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        """
        ينشئ الحالة الداخلية ويثبت dependencies اللازمة للعملية ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى __init__؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد None أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0
        self.title: str | None = None
        self._in_title = False
        self._title_parts: list[str] = []
        self._active_heading: str | None = None
        self._heading_parts: list[str] = []
        self.headings: list[str] = []

    def handle_starttag(self, tag, attrs):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى handle_starttag؛ المدخلات المهمة: tag، attrs.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        tag = tag.casefold()

        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
            return

        if self._skip_depth:
            return

        if tag == "title":
            self._in_title = True

        if tag in self.HEADING_TAGS:
            self._active_heading = tag
            self._heading_parts = []

        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى handle_endtag؛ المدخلات المهمة: tag.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
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

        if tag in self.HEADING_TAGS and self._active_heading == tag:
            heading = normalize_text(" ".join(self._heading_parts))
            if heading:
                self.headings.append(heading)
            self._active_heading = None
            self._heading_parts = []

        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data):
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى handle_data؛ المدخلات المهمة: data.
        تعيد نتيجة العملية الحالية أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        if self._skip_depth:
            return

        value = data.strip()

        if not value:
            return

        if self._in_title:
            self._title_parts.append(value)

        if self._active_heading:
            self._heading_parts.append(value)

        self._parts.append(value)
        self._parts.append(" ")

    def text(self) -> str:
        """
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى text؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
        تعيد str أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
        """
        return normalize_text("".join(self._parts))


class KnowledgeContentParser:
    """
    يمثل KnowledgeContentParser مسؤولية محددة داخل طبقة Application capability / knowledge.

    مسؤوليته تنسيق أو تمثيل الجزء الظاهر في هذا الملف، ويستخدمه أدوات الإدارة أو Retrieval
    ويعتمد على لا يرث contract خارجيًا وعلى dependencies التي يمررها الـcomposition أو يستوردها الملف.
    لا ينبغي أن يتولى مسؤوليات الطبقات الأخرى مثل SQL/SSH/LLM أو authorization
    إلا إذا ظهر ذلك صراحةً في implementation الحالي.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى parse؛ المدخلات المهمة: content، canonical_uri، media_type، title_hint.
        تعيد ParsedKnowledgeDocument أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        يحوّل البيانات إلى الشكل الذي تحتاجه الطبقة التالية مع الحفاظ على provenance ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى parse_file؛ المدخلات المهمة: path، canonical_uri، title_hint.
        تعيد ParsedKnowledgeDocument أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى _parse_text؛ المدخلات المهمة: content، canonical_uri، media_type، title_hint.
        تعيد ParsedKnowledgeDocument أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى _parse_html؛ المدخلات المهمة: content، canonical_uri، media_type، title_hint.
        تعيد ParsedKnowledgeDocument أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
        ينفذ العملية الخاصة بهذه الطبقة ويعيد ناتجها إلى caller ضمن طبقة Application capability / knowledge.

        تُستدعى عندما يصل workflow إلى _parse_pdf؛ المدخلات المهمة: content، canonical_uri، title_hint.
        تعيد ParsedKnowledgeDocument أو تحدث الأثر الذي يحدده contract هذه الدالة.
        قد يرفع exception أو يعيد نتيجة فشل عند عدم تحقق المدخلات أو فشل dependency خارجية.
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
