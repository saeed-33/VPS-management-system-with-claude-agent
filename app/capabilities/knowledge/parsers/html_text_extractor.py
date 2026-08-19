"""استخراج النص المرئي والعناوين من HTML."""
from __future__ import annotations
from html.parser import HTMLParser
from .text_normalization import normalize_text

class _HTMLTextExtractor(HTMLParser):
    """
    يستخرج نص HTML والعنوان والعناوين مع تجاهل عناصر السكربت والتنسيق.
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
        يهيئ محلل HTML ومكدسات النص والعنوان والعناوين التي سيستخرجها.
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
        يعالج بداية عنصر HTML لتحديد عناصر التجاهل والعنوان والقسم والفاصل النصي.
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
        يغلق حالة عنصر HTML ويحفظ العنوان أو العنوان الفرعي ويضيف فاصل الكتلة عند الحاجة.
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
        يجمع النص المرئي داخل HTML ويغذي العنوان والقسم النشطين مع تجاهل العناصر المحظورة.
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
        يعيد النص المرئي المستخرج من HTML بعد تطبيعه.
        """
        return normalize_text("".join(self._parts))
