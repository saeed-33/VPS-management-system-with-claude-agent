"""تقطيع محتوى المعرفة مع مراعاة البنية والعناوين."""
from __future__ import annotations
import re
from app.capabilities.knowledge.ingestion_contracts.chunk_draft import KnowledgeChunkDraft
from .block import _Block
from .config import KnowledgeChunkerConfig
from .constants import _MARKDOWN_HEADING_RE, _SENTENCE_BOUNDARY_RE
class StructureAwareKnowledgeChunker:
    """
    يقسم الوثيقة إلى مقاطع تراعي الفقرات والعناوين والصفحات وحدود الحجم.
    """
    def __init__(
        self,
        config: KnowledgeChunkerConfig | None = None,
    ) -> None:
        """
        يحفظ إعدادات التقطيع المقدمة أو ينشئ الإعدادات الافتراضية.
        """
        self._config = config or KnowledgeChunkerConfig()
    def chunk_document(
        self,
        *,
        text: str,
        metadata: dict | None = None,
    ) -> tuple[KnowledgeChunkDraft, ...]:
        """
        يبني الكتل ويقسم الكبيرة ثم يدمجها ضمن الحدود مع الاحتفاظ بتداخل وسياق العنوان والصفحة.
        """
        blocks = self._build_blocks(
            text=text,
            metadata=dict(metadata or {}),
        )

        if not blocks:
            return ()

        chunks: list[KnowledgeChunkDraft] = []
        current: list[_Block] = []

        for block in blocks:
            for piece in self._split_oversized_block(block):
                candidate = [*current, piece]

                if (
                    current
                    and self._joined_size(candidate)
                    > self._config.target_chars
                ):
                    chunks.append(
                        self._make_chunk(
                            index=len(chunks),
                            blocks=current,
                        )
                    )

                    current = self._overlap_blocks(current)
                    candidate = [*current, piece]

                    if (
                        current
                        and self._joined_size(candidate)
                        > self._config.max_chars
                    ):
                        current = []

                current.append(piece)

        if current:
            final_chunk = self._make_chunk(
                index=len(chunks),
                blocks=current,
            )

            if (
                chunks
                and len(final_chunk.content) < self._config.min_chars
            ):
                previous = chunks[-1]
                merged = (
                    previous.content.rstrip()
                    + "\n\n"
                    + final_chunk.content.lstrip()
                )

                if len(merged) <= self._config.max_chars:
                    chunks[-1] = KnowledgeChunkDraft(
                        chunk_index=previous.chunk_index,
                        content=merged,
                        section_title=(
                            previous.section_title
                            or final_chunk.section_title
                        ),
                        page_number=(
                            previous.page_number
                            if previous.page_number == final_chunk.page_number
                            else None
                        ),
                        metadata={
                            **previous.metadata,
                            "merged_tail": True,
                        },
                    )
                else:
                    chunks.append(final_chunk)
            else:
                chunks.append(final_chunk)

        return tuple(chunks)
    def _build_blocks(
        self,
        *,
        text: str,
        metadata: dict,
    ) -> list[_Block]:
        """
        يستخدم صفحات PDF عند توفرها أو يحلل النص والفقرات والعناوين إلى كتل داخلية.
        """
        pages = metadata.get("pages")

        if isinstance(pages, list) and pages:
            blocks: list[_Block] = []

            for item in pages:
                if not isinstance(item, dict):
                    continue

                page_text = str(item.get("text") or "").strip()

                if not page_text:
                    continue

                raw_page = item.get("page_number")
                page_number = (
                    int(raw_page)
                    if raw_page is not None
                    else None
                )

                blocks.extend(
                    self._paragraph_blocks(
                        page_text,
                        page_number=page_number,
                    )
                )

            if blocks:
                return blocks

        headings = {
            str(value).strip()
            for value in metadata.get("html_headings", [])
            if str(value).strip()
        }

        return self._paragraph_blocks(
            text,
            known_headings=headings,
        )

    def _paragraph_blocks(
        self,
        text: str,
        *,
        page_number: int | None = None,
        known_headings: set[str] | None = None,
    ) -> list[_Block]:
        """
        يقسم النص إلى فقرات ويحدّث القسم الحالي عند مواجهة عنوان Markdown أو HTML معروف.
        """
        known_headings = known_headings or set()
        blocks: list[_Block] = []
        current_section: str | None = None

        raw_blocks = [
            value.strip()
            for value in re.split(r"\n\s*\n", text)
            if value.strip()
        ]

        for raw in raw_blocks:
            markdown_match = _MARKDOWN_HEADING_RE.match(raw)

            if markdown_match:
                current_section = markdown_match.group(1).strip()
                continue

            if raw in known_headings:
                current_section = raw
                continue

            blocks.append(
                _Block(
                    text=raw,
                    section_title=current_section,
                    page_number=page_number,
                )
            )

        return blocks
    def _split_oversized_block(
        self,
        block: _Block,
    ) -> list[_Block]:
        """
        يقسم الكتلة التي تتجاوز الحد الأقصى عند حدود الجمل أو إلى شرائح ثابتة عند تعذر ذلك.
        """
        if len(block.text) <= self._config.max_chars:
            return [block]

        sentences = [
            value.strip()
            for value in _SENTENCE_BOUNDARY_RE.split(block.text)
            if value.strip()
        ]

        if len(sentences) <= 1:
            return [
                _Block(
                    text=block.text[
                        start:start + self._config.max_chars
                    ].strip(),
                    section_title=block.section_title,
                    page_number=block.page_number,
                )
                for start in range(
                    0,
                    len(block.text),
                    self._config.max_chars,
                )
                if block.text[
                    start:start + self._config.max_chars
                ].strip()
            ]

        result: list[_Block] = []
        current: list[str] = []

        for sentence in sentences:
            proposed = " ".join([*current, sentence])

            if current and len(proposed) > self._config.max_chars:
                result.append(
                    _Block(
                        text=" ".join(current),
                        section_title=block.section_title,
                        page_number=block.page_number,
                    )
                )
                current = [sentence]
            else:
                current.append(sentence)

        if current:
            result.append(
                _Block(
                    text=" ".join(current),
                    section_title=block.section_title,
                    page_number=block.page_number,
                )
            )

        return result

    def _overlap_blocks(
        self,
        blocks: list[_Block],
    ) -> list[_Block]:
        """
        يختار ذيل الكتل السابقة الذي يدخل كتلة التداخل للحفاظ على السياق بين المقاطع.
        """
        if self._config.overlap_chars == 0:
            return []

        selected: list[_Block] = []
        size = 0

        for block in reversed(blocks):
            block_size = len(block.text)

            if (
                selected
                and size + 2 + block_size
                > self._config.overlap_chars
            ):
                break

            selected.append(block)
            size += block_size + (2 if selected[:-1] else 0)

            if size >= self._config.overlap_chars:
                break

        selected.reverse()
        return selected

    @staticmethod
    def _joined_size(blocks: list[_Block]) -> int:
        """
        يحسب طول النص الناتج عن وصل مجموعة كتل بفواصل الفقرات.
        """
        if not blocks:
            return 0

        return (
            sum(len(block.text) for block in blocks)
            + (2 * (len(blocks) - 1))
        )

    @staticmethod
    def _make_chunk(
        *,
        index: int,
        blocks: list[_Block],
    ) -> KnowledgeChunkDraft:
        """
        ينشئ مسودة مقطع من الكتل ويجمع عناوين الأقسام وأرقام الصفحات في بياناته الوصفية.
        """
        sections = [
            block.section_title
            for block in blocks
            if block.section_title
        ]

        pages = {
            block.page_number
            for block in blocks
            if block.page_number is not None
        }

        return KnowledgeChunkDraft(
            chunk_index=index,
            content="\n\n".join(
                block.text
                for block in blocks
            ),
            section_title=(
                sections[-1]
                if sections
                else None
            ),
            page_number=(
                next(iter(pages))
                if len(pages) == 1
                else None
            ),
            metadata={
                "section_titles": list(dict.fromkeys(sections)),
                "page_numbers": sorted(pages),
            },
        )
